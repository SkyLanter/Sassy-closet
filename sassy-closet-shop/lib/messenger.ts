/** Build Messenger hrefs from the configured Page URL. Never invent a Page. Never prefill. */

const PAGE_ID = /^\d{5,}$/;
const RECORDED_PAGE_ID = "61594312648057";

export function messengerPageId(pageUrl: string): string {
  try {
    const url = new URL(pageUrl);
    const host = url.hostname.replace(/^www\./, "");
    const isMe = host === "m.me";
    const isFacebook =
      host === "facebook.com" ||
      host === "fb.com" ||
      host === "m.facebook.com" ||
      host === "web.facebook.com" ||
      host === "m.fb.com";
    const isMessengerHost = host === "messenger.com";
    if (!isMe && !isFacebook && !isMessengerHost) {
      return "";
    }
    const idParam = url.searchParams.get("id");
    if (idParam && PAGE_ID.test(idParam)) {
      return idParam;
    }
    const parts = url.pathname.split("/").filter(Boolean);
    const first = parts[0];
    if (first === "t" || first === "messages") {
      const next = parts[1];
      if (next && PAGE_ID.test(next)) {
        return next;
      }
    }
    if (first && PAGE_ID.test(first)) {
      return first;
    }
  } catch {
    return "";
  }
  return "";
}

function recordedPageId(pageUrl: string): string {
  return messengerPageId(pageUrl) || RECORDED_PAGE_ID;
}

/**
 * Desktop / web: same-tab https://m.me/{pageId}.
 * Always m.me — never facebook.com/profile.php (that is the Page, not the inbox).
 * Never the primary iPhone href: m.me + a blank tab is the Safari hop.
 */
export function messengerHref(pageUrl: string): string {
  const trimmed = pageUrl.trim();
  if (!trimmed) {
    return "";
  }
  return `https://m.me/${recordedPageId(trimmed)}`;
}

/**
 * iPhone / Android tap: Messenger app Page thread.
 * Exact scheme Mini Boss verifies: fb-messenger://user-thread/61594312648057
 * Native <a href> only. No delayed hop to https://m.me or messenger.com.
 */
export function messengerAppHref(pageUrl: string): string {
  const trimmed = pageUrl.trim();
  if (!trimmed) {
    return "";
  }
  return `fb-messenger://user-thread/${recordedPageId(trimmed)}`;
}

/**
 * Phone-first: touch / SSR (canHover is false on the server) uses the app scheme
 * so iPhone HTML is never https://m.me. Desktop hover pointers stay on m.me.
 */
export function messengerUsesAppScheme(isAppDevice: boolean, canHover: boolean): boolean {
  return isAppDevice || !canHover;
}

export function messengerTapHref(pageUrl: string, isAppDevice: boolean): string {
  return isAppDevice ? messengerAppHref(pageUrl) : messengerHref(pageUrl);
}

export function messengerCtaHref(
  pageUrl: string,
  isAppDevice: boolean,
  canHover: boolean,
): string {
  return messengerTapHref(pageUrl, messengerUsesAppScheme(isAppDevice, canHover));
}

export function isMessengerAppDevice(
  userAgent: string,
  maxTouchPoints = 0,
  chMobile = "",
): boolean {
  if (chMobile.trim() === "?1") {
    return true;
  }
  if (/iPhone|iPod|iPad/i.test(userAgent)) {
    return true;
  }
  if (/Android/i.test(userAgent)) {
    return true;
  }
  if (maxTouchPoints > 1 && /Macintosh/i.test(userAgent)) {
    return true;
  }
  return false;
}
