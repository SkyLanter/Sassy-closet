/**
 * The customer shop does not serve repo fixtures.
 *
 * `public/data/taobao_confirm_seed.json` is a Taobao supplier seed: supplier
 * links, shop names, and CNY supplier prices for every mã. Next serves anything
 * under `public/`, so `/data/taobao_confirm_seed.json` was a public 200 even
 * though customer HTML strips `sourceLink` and `scripts/privacy_scan.py` flags
 * those links. The app has no `/data` route, so the whole prefix is closed here.
 */

/** Path segments after decoding, with `.` skipped and `..` collapsed. */
function pathSegments(pathname: string): string[] | null {
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return null;
  }
  if (decoded.includes("\0")) {
    return null;
  }
  const segments: string[] = [];
  for (const raw of decoded.split("/")) {
    if (raw === "" || raw === ".") {
      continue;
    }
    if (raw === "..") {
      segments.pop();
      continue;
    }
    segments.push(raw);
  }
  return segments;
}

/** True for `/data`, `/data/`, and any `/data/...` spelling of the seed folder. */
export function isSeedAssetPath(pathname: string): boolean {
  const segments = pathSegments(pathname);
  if (!segments || segments.length === 0) {
    return false;
  }
  return (segments[0] ?? "").toLowerCase() === "data";
}
