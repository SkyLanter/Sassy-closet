import { getProductsUncached } from "@/lib/products";
import { getCatalogStorageInfo } from "@/lib/catalog-store";
import { NO_STORE_HEADERS } from "@/lib/http-no-store";
import {
  applyStageResult,
  parseIntakeReceivePayload,
  stageIntakeSubmission,
  type CatalogMaIndex,
} from "@/lib/intake-receive";
import { readStagedForReceive, writeStagedRecord } from "@/lib/intake-staged-store";

export const dynamic = "force-dynamic";
export const revalidate = 0;

/**
 * POST /api/intake/receive — the sell-site intake receiver (PR #42's other end).
 *
 * The intake site calls this the moment Nhung submits. Auth is a shared key;
 * it NEVER fails open (no key configured → 503).
 *
 * This endpoint only STAGES. It never publishes to the live catalog, never
 * merges, never marks Square stock. Staged records sit at needs_research with
 * priceUsd null ("Inbox giá") until a human verifies the fields.
 */

function readReceiveKey(): string {
  return process.env.INTAKE_RECEIVE_KEY?.trim() ?? "";
}

function unauthorized(): Response {
  return Response.json(
    { ok: false, error: "Unauthorized." },
    { status: 401, headers: NO_STORE_HEADERS },
  );
}

function checkAuth(request: Request): Response | null {
  const key = readReceiveKey();
  if (!key) {
    // Never fail open: without a configured key nothing is accepted.
    return Response.json(
      { ok: false, error: "Intake receiver is not configured." },
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }
  const bearer = request.headers.get("authorization") ?? "";
  const automationKey = request.headers.get("x-automation-key") ?? "";
  // The PR #42 sender transmits both headers; accept either.
  if (bearer === `Bearer ${key}` || automationKey === key) {
    return null;
  }
  return unauthorized();
}

export async function GET() {
  return Response.json(
    { ok: false, error: "Use POST with the intake shared key." },
    { status: 405, headers: NO_STORE_HEADERS },
  );
}

export async function POST(request: Request) {
  const auth = checkAuth(request);
  if (auth) return auth;

  const storage = getCatalogStorageInfo();
  if (!storage.canWrite) {
    return Response.json(
      { ok: false, error: "Intake staging has no store on this deployment." },
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json(
      { ok: false, error: "Body must be JSON." },
      { status: 400, headers: NO_STORE_HEADERS },
    );
  }

  const parsed = parseIntakeReceivePayload(body);
  if (!parsed.ok) {
    return Response.json(
      { ok: false, error: parsed.error },
      { status: 400, headers: NO_STORE_HEADERS },
    );
  }

  // Mã/link immutability needs the live catalog's index.
  let catalogIndex: CatalogMaIndex = { mas: new Set(), links: new Map() };
  try {
    const products = await getProductsUncached();
    const mas = new Set<string>();
    const links = new Map<string, string>();
    for (const p of products) {
      mas.add(p.ma);
      if (p.sourceLink) links.set(p.ma, p.sourceLink);
    }
    catalogIndex = { mas, links };
  } catch (error) {
    console.error("[intake-receive] catalog index read failed.", error);
    return Response.json(
      { ok: false, error: "Could not read the catalog; submission not staged." },
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }

  const now = new Date().toISOString();
  const doc = await readStagedForReceive();
  const result = stageIntakeSubmission(doc.records, parsed.payload, catalogIndex, now);
  if (!result.ok) {
    return Response.json(
      { ok: false, error: result.error },
      { status: 409, headers: NO_STORE_HEADERS },
    );
  }

  const next = applyStageResult(doc, result, now);
  try {
    await writeStagedRecord(next);
  } catch (error) {
    console.error("[intake-receive] staged write failed.", error);
    return Response.json(
      { ok: false, error: "Could not persist the staged submission." },
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }

  return Response.json(
    {
      ok: true,
      status: result.status,
      ma: result.record.ma,
      stage: result.record.stage,
      price: "Inbox giá",
      staged_at: result.record.updatedAt,
      submission_count: result.record.submissionCount,
    },
    { status: 200, headers: NO_STORE_HEADERS },
  );
}
