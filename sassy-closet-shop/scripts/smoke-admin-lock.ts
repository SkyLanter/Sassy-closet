import { randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import {
  ADMIN_SESSION_COOKIE,
  ADMIN_SESSION_MAX_AGE_SECONDS,
  adminAuthConfigured,
  adminSessionCookie,
  constantTimeEqual,
  createAdminSessionToken,
  passwordMatches,
  verifyAdminSession,
} from "../lib/admin-auth";
import { adminGateDecision, safeAdminNext } from "../lib/admin-gate";
import {
  LOGIN_FAILURE_DELAY_MS,
  loginAttemptAllowed,
  recordLoginFailure,
  recordLoginSuccess,
  resetLoginBuckets,
} from "../lib/admin-login-rate";
import robots from "../app/robots";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const savedPassword = process.env.ADMIN_PASSWORD;
const savedSecret = process.env.ADMIN_SESSION_SECRET;

function restoreEnv(): void {
  if (savedPassword === undefined) {
    delete process.env.ADMIN_PASSWORD;
  } else {
    process.env.ADMIN_PASSWORD = savedPassword;
  }
  if (savedSecret === undefined) {
    delete process.env.ADMIN_SESSION_SECRET;
  } else {
    process.env.ADMIN_SESSION_SECRET = savedSecret;
  }
}

try {
  delete process.env.ADMIN_PASSWORD;
  delete process.env.ADMIN_SESSION_SECRET;
  if (adminAuthConfigured() || createAdminSessionToken(0) || passwordMatches("x") || verifyAdminSession("a.b")) {
    fail("missing admin env must fail closed");
  }

  const password = randomBytes(24).toString("base64url");
  const secret = randomBytes(32).toString("base64url");
  process.env.ADMIN_PASSWORD = password;
  process.env.ADMIN_SESSION_SECRET = secret;
  if (!adminAuthConfigured()) {
    fail("both env vars must count as configured");
  }
  if (!passwordMatches(password) || passwordMatches(`${password}x`) || passwordMatches("")) {
    fail("password compare must accept only the configured value");
  }
  if (!constantTimeEqual("same", "same") || constantTimeEqual("short", "much-longer-value")) {
    fail("constant-time compare must handle equal and unequal lengths");
  }

  const issuedAt = 1_700_000_000_000;
  const token = createAdminSessionToken(issuedAt);
  if (!token || !verifyAdminSession(token, issuedAt + 1_000)) {
    fail("session token must round-trip");
  }
  if (verifyAdminSession(token, issuedAt + (ADMIN_SESSION_MAX_AGE_SECONDS + 5) * 1000)) {
    fail("expired session must fail");
  }
  if (verifyAdminSession(`${token}x`, issuedAt + 1_000)) {
    fail("tampered session must fail");
  }
  process.env.ADMIN_PASSWORD = `${password}rotated`;
  if (verifyAdminSession(token, issuedAt + 1_000)) {
    fail("password rotation must invalidate sessions");
  }
  process.env.ADMIN_PASSWORD = password;

  const cookie = adminSessionCookie(token);
  if (
    cookie.name !== ADMIN_SESSION_COOKIE ||
    cookie.httpOnly !== true ||
    cookie.secure !== true ||
    cookie.sameSite !== "lax" ||
    cookie.path !== "/" ||
    cookie.maxAge !== ADMIN_SESSION_MAX_AGE_SECONDS
  ) {
    fail("session cookie must be httpOnly, Secure, SameSite=Lax, 30 days");
  }

  if (LOGIN_FAILURE_DELAY_MS < 500) {
    fail("failed logins must wait");
  }
  resetLoginBuckets();
  const ip = "203.0.113.9";
  const start = 1_700_000_000_000;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    const decision = loginAttemptAllowed(ip, start + attempt);
    if (!decision.ok) {
      fail("throttle must allow the first five failures");
    }
    recordLoginFailure(ip, start + attempt);
  }
  const locked = loginAttemptAllowed(ip, start + 10);
  if (locked.ok) {
    fail("sixth attempt must be rate limited");
  }
  recordLoginSuccess(ip);
  const cleared = loginAttemptAllowed(ip, start + 10);
  if (!cleared.ok) {
    fail("a successful login must clear the throttle");
  }

  if (safeAdminNext("/admin/edit/A01") !== "/admin/edit/A01") {
    fail("edit path must stay on the desk");
  }
  if (
    safeAdminNext("https://evil.example/admin") !== "/admin" ||
    safeAdminNext("//evil.example") !== "/admin" ||
    safeAdminNext("/admin/../") !== "/admin" ||
    safeAdminNext("/m/A01") !== "/admin" ||
    safeAdminNext("/admin/login") !== "/admin"
  ) {
    fail("next= must not leave the desk");
  }

  if (adminGateDecision("/m/A01", "GET", false) !== "public") {
    fail("product pages stay public");
  }
  if (adminGateDecision("/admin", "GET", false) !== "deny") {
    fail("logged-out /admin must deny");
  }
  if (adminGateDecision("/admin/login", "GET", false) !== "allow") {
    fail("login page must stay reachable");
  }
  if (adminGateDecision("/api/admin/save", "POST", false) !== "deny") {
    fail("logged-out save must deny");
  }
  if (adminGateDecision("/api/admin/login", "POST", false) !== "allow") {
    fail("login API must stay reachable");
  }
  if (adminGateDecision("/api/admin/logout", "POST", false) !== "deny") {
    fail("logged-out logout must deny");
  }
  if (adminGateDecision("/api/admin/catalog", "GET", true) !== "allow") {
    fail("signed-in catalog read must allow");
  }

  const hostCookie = adminSessionCookie("host-only");
  if ("domain" in hostCookie) {
    fail("admin cookie must stay host-only so both shop hostnames can sign in");
  }
  const authSource = read("lib/admin-auth.ts");
  if (!authSource.includes("timingSafeEqual") || !authSource.includes('createHash("sha256")')) {
    fail("compare must hash then timingSafeEqual");
  }
  if (authSource.includes("domain:")) {
    fail("admin cookie must not set a Domain attribute");
  }
  const loginRoute = read("app/api/admin/login/route.ts");
  const proxySource = read("proxy.ts");
  for (const source of [loginRoute, proxySource]) {
    if (source.includes("sassy-closet-shop.vercel.app") || source.includes("sassycloset.vercel.app")) {
      fail("login redirects must stay on the request host");
    }
  }
  if (/length ===[\s\S]{0,120}timingSafeEqual/.test(authSource)) {
    fail("do not skip timingSafeEqual when lengths differ");
  }

  const header = read("components/header.tsx");
  const shopLayout = read("app/(shop)/layout.tsx");
  if (header.includes("admin-entry") || header.includes("Shop tools") || header.includes("/api/admin")) {
    fail("public header must not reference admin UI");
  }
  if (
    shopLayout.includes("admin-entry") ||
    shopLayout.includes("shop-admin-chrome") ||
    shopLayout.includes("Shop tools")
  ) {
    fail("shop layout must not statically import the admin entry");
  }
  if (!shopLayout.includes("hasAdminSession") || !shopLayout.includes("ShopAdminGate")) {
    fail("shop layout must mount admin chrome only for a session");
  }
  const gate = read("components/shop-admin-gate.tsx");
  if (gate.includes("Shop tools") || gate.includes("/api/admin") || gate.includes("Open admin")) {
    fail("admin gate loader must not inline admin copy");
  }

  const rules = robots().rules;
  const rule = Array.isArray(rules) ? rules[0] : rules;
  const disallow = JSON.stringify(rule?.disallow ?? "");
  if (!disallow.includes("/admin") || !disallow.includes("/admin/") || !disallow.includes("/api/")) {
    fail("robots.txt must disallow /admin and /api/");
  }

  const envExample = read(".env.example");
  if (envExample.includes("ADMIN_PASSWORD=")) {
    fail("do not put an admin password assignment in .env.example");
  }

  console.log("admin lock ok");
} finally {
  restoreEnv();
  resetLoginBuckets();
}
