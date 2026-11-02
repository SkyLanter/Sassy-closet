import { NO_STORE_HEADERS } from "@/lib/http-no-store";

/** Missing mã or category. Not a JPEG, and not cacheable. */
export function shareNotFound(): Response {
  return new Response("Not found", {
    status: 404,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      ...NO_STORE_HEADERS,
    },
  });
}

/** Catalog read failed. Do not paint the home card under this URL. */
export function shareUnavailable(): Response {
  return new Response("Share card unavailable", {
    status: 503,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      ...NO_STORE_HEADERS,
    },
  });
}
