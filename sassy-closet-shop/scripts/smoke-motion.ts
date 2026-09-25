import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import path from "node:path";
import { clampedReelIndexForColor, firstReelIndexForColor, productGalleryReel } from "../lib/gallery-reel";
import { clampGalleryIndex, galleryPeekEdge, GALLERY_ROLL_MS } from "../lib/gallery-snap";
import {
  CONTENT_WAVE_HOLD_MS,
  CONTENT_WAVE_INTRO_RATIO,
  CONTENT_WAVE_MS,
  contentWaveDurationMs,
} from "../lib/content-wave";
import { COLOR_FADE_SECONDS, FILTER_FADE_SECONDS, FILTER_SLIDE_SECONDS, fadeUp } from "../lib/motion";
import { coverSrcForColor, imagesForColor } from "../lib/product-media";
import { parseCatalogDocument } from "../lib/product-parse";
import { shopVisibleProducts } from "../lib/site-settings";
import type { Product } from "../lib/types";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const css = read("app/globals.css");
if (!css.includes("@media (prefers-reduced-motion: no-preference)")) {
  fail("Looped motion must live under prefers-reduced-motion: no-preference");
}
if (!css.includes("-webkit-tap-highlight-color: transparent")) {
  fail("iOS tap highlight must stay off so gold focus is the only flash");
}
const reduceMotionCss = css.split("@media (prefers-reduced-motion: reduce)")[1] ?? "";
if (!reduceMotionCss.includes(".tab-scroll")) {
  fail("Reduce Motion must kill tab-scroll smoothing");
}
if (!reduceMotionCss.includes(".content-wave-layer")) {
  fail("Reduce Motion must hide the sheen layer");
}
if (css.includes("filter: url(#ky-gold-goo)") || css.includes(".ky-gold-goo") || css.includes("ky-rim-spin")) {
  fail("Gold goo and rim spin must stay gone");
}
if (!css.includes(".featured-pour") || !css.includes("clip-path: none !important")) {
  fail("Reduce Motion must kill leftover clip/transform on the looks stack");
}
if (css.includes('[style*="ky-gold-goo"]') || css.includes("feGaussianBlur")) {
  fail("Goo SVG filter must not return");
}
if (!css.includes(".featured-pour-stack") || !css.includes("overflow: hidden")) {
  fail("Looks stack must overlap in an overflow-hidden cell");
}
if (!css.includes(".featured-pour-stack") || !css.includes(".featured-pour-layer")) {
  fail("Looks filter must stack overlapping layers for a quiet crossfade");
}
if (css.includes("gallery-water-sheen") || css.includes("gallery-water-roll") || css.includes("data-water-roll")) {
  fail("Gallery water sheen must stay gone");
}
if (css.includes(".content-wave-sheet") || css.includes("@keyframes content-wave-ltr") || css.includes("content-wave-echo")) {
  fail("Watery glass ribbon (.content-wave-sheet / echo / content-wave-ltr) must stay gone");
}
if (css.includes(".content-wave-heart") || css.includes("@keyframes content-wave-hearts-ltr") || css.includes("GlassHeart")) {
  fail("Heart curtain must stay gone");
}
if (!css.includes(".content-wave-sheen") || !css.includes("@keyframes content-wave-sheen-ltr")) {
  fail("Looks must sweep a slow L→R soft sheen");
}
if (!css.includes("mix-blend-mode: soft-light")) {
  fail("Content sheen must stay a see-through soft-light sweep");
}
if (css.includes("translateX(520%)") || css.includes("--wave-mask") || css.includes("content-wave-ripple")) {
  fail("Wave mask, 520% travel, and ripple must stay gone");
}
if (css.includes("animation-duration: 480ms") && css.includes("animation-timing-function: linear")) {
  fail("Linear 480ms glass wave travel must stay gone");
}
if (!css.includes("rgb(255 255 255 / 0.48)") || !css.includes("rgb(17 17 17 / 0.32)")) {
  fail("Boutique frost must stay see-through Regular 48% and Clear 32%");
}
const sheetRule = css.split(".liquid-glass-sheet {")[1]?.split("}")[0] ?? "";
if (!sheetRule.includes("background: rgb(255 255 255 / 0.48)") || !sheetRule.includes("var(--glass-blur)") || !sheetRule.includes("var(--glass-sat)")) {
  fail("Modal sheets must share Regular 48% frost and --glass-blur so photos show through");
}
if (!sheetRule.includes("--muted: #2e2e2e")) {
  fail("Modal sheets must darken muted ink for contrast on frost");
}
if (css.includes("background: rgb(255 255 255 / 0.55)")) {
  fail("Modal sheets must not use milky 55% fog");
}
if (css.includes("blur(40px)")) {
  fail("Modal sheets must use --glass-blur, not a 40px milk");
}
const chipRule = css.split(".liquid-glass-chip,\n.ky-color-chip {")[1]?.split("}")[0] ?? "";
if (!chipRule.includes("background: rgb(255 255 255 / 0.42)") || !chipRule.includes("var(--glass-blur)") || !chipRule.includes("var(--glass-sat)")) {
  fail("Color chips must share Regular glass blur, not a 16px fog disc");
}
if (!chipRule.includes("--muted: #2e2e2e")) {
  fail("Color chips must darken muted ink for contrast on frost");
}
if (css.includes("blur(16px)")) {
  fail("Chip frost must use --glass-blur, not a 16px milk");
}
const cssWithoutLookSheen = css.replace(/\.content-wave-sheen\s*\{[^}]*\}/g, "");
if (cssWithoutLookSheen.includes("mix-blend-mode: soft-light")) {
  fail("Do not soft-light paper onto clothes (white washout)");
}
if (css.includes("mix-blend-mode: plus-lighter")) {
  fail("Looks motion must not plus-lighter bleach the garment");
}
if (!css.includes("isolation: isolate")) {
  fail("Looks stack must isolate overlapping layers");
}
if (css.includes("animation: shimmer-slide 1.3s ease-in-out infinite")) {
  fail("Idle shimmer must not loop");
}
if (!css.includes("shimmer-slide 1.1s ease-out 1 forwards")) {
  fail("Cover shimmer is one-shot, then still");
}
const shimmerBlock = css.split(".shimmer")[2] ?? "";
if (shimmerBlock.includes("infinite") && !css.includes("no-preference")) {
  fail("Infinite shimmer must not run without a no-preference query");
}
if (!css.includes("@keyframes announce-fade") || !css.includes("@keyframes shimmer-slide")) {
  fail("Do not rename or delete announce-fade / shimmer-slide");
}
if (css.includes("@keyframes cta-flash") || css.includes(".cta-shine")) {
  fail("CTA shine/flash must stay gone");
}
if (!css.includes("@view-transition") || !css.includes("navigation: auto")) {
  fail("Lookbook documents must opt into MPA view transitions");
}
if (!css.includes("pointer-events: none") || !css.includes("view-transition-group(site-header)")) {
  fail("Header VT overlay contract must stay");
}

const image = read("components/product-image.tsx");
if (image.includes("opacity-0")) {
  fail("Cover <img> must not use opacity-0 (paints without JS)");
}
if (!image.includes("viewTransitionName: `product-${product.ma}`")) {
  fail("Card/PDP cover wrapper must keep view-transition-name product-{THIS mã}");
}
if (!image.includes("motion-safe:hover-hover:group-hover:scale-[1.04]")) {
  fail("Cover zoom must be motion-safe and hover-only (no iPhone sticky hover)");
}
if (image.includes("scale-[1.08]") || image.includes("duration-[800ms]")) {
  fail("Cover zoom must stay quiet (1.04 / 500ms), not an 8% Ken Burns");
}
if (!image.includes("motion-safe:duration-500")) {
  fail("Cover zoom duration must match the quiet card lift");
}
if (!image.includes("object-top")) {
  fail("Look covers must pin object-top so garments are not cropped at the neck");
}
if (!image.includes("draggable={false}") || !image.includes("select-none")) {
  fail("Cover photos must not drag off the card on iOS");
}
if (!image.includes('alt=""')) {
  fail("Card covers must stay decorative inside the named look link");
}
if (!image.includes("decorative")) {
  fail("Card placeholder fallback must stay decorative inside the named look link");
}
if (!image.includes("select-none flex-col")) {
  fail("Placeholder tiles must not select the letter on tap");
}
if (!image.includes("className=\"shimmer")) {
  fail("Card cover must keep the shimmer layer");
}

const card = read("components/product-card.tsx");
if (!card.includes("motion-safe:hover-hover:group-hover:-translate-y-1.5")) {
  fail("Card lift must be motion-safe and hover-only (no iPhone sticky hover)");
}
if (!card.includes("touch-manipulation") || !card.includes("min-w-0")) {
  fail("Look cards must stay tap targets and not overflow the grid");
}
if (!card.includes("mt-2 min-w-0 px-0.5")) {
  fail("Look-card color rails must shrink inside the card instead of blowing the grid");
}
if (!card.includes("group block touch-manipulation select-none")) {
  fail("Look card links must not select names on tap");
}
if (css.includes("@keyframes gallery-water-roll") || css.includes('[data-water-roll="1"]')) {
  fail("Color-roll glass sheen must stay gone");
}
if (!card.includes("viewTransitionName: `product-${product.ma}`") || !card.includes("aspect-[3/4]")) {
  fail("Card 3/4 frame must keep product-{THIS mã} (stable, not on the fade layer)");
}
if (!card.includes("leading-[1.12]") || card.includes("leading-none")) {
  fail("Card serif names must not clip descenders with leading-none");
}
if (!card.includes("scale-x-100") || !card.includes("bg-gold/45")) {
  fail("Look cards must keep a quiet gold hairline on touch");
}
if (!card.includes('bg-gold/45" aria-hidden')) {
  fail("Look card gold hairline must stay decorative");
}
if (!card.includes("liquid-glass-rim") || !card.includes("bg-gradient-to-t")) {
  fail("Look cards must keep a glass rim overlay and a decorative hover film");
}
if (!card.includes("from-ink/10") || !card.includes("group-hover:opacity-70")) {
  fail("Look card hover film must stay a quiet ink veil");
}
if (card.includes("from-ink/16") || card.includes("group-hover:opacity-100")) {
  fail("Look card hover film must not dump a full ink wash on the garment");
}
if (card.includes("group-hover:scale-x-100")) {
  fail("Look card gold hairline must not be hover-only");
}
if (!card.includes("named={false}")) {
  fail("Card must not put the VT name on the remounting <img> layer");
}
if (!card.includes("useState<string | null>(null)")) {
  fail("Card chips start unset — do not remount the cover on a null colorId tap");
}
if (!card.includes("product.colors.length > 0")) {
  fail("Card color chips only when colors[] exist");
}
if (card.includes("AnimatePresence") || card.includes("colorCrossfade") || card.includes("key={preview")) {
  fail("Card color tap must roll this mã’s reel, not remount the cover");
}
if (!card.includes("clampedReelIndexForColor") || !card.includes("productGalleryReel") || !card.includes("ky-card-reel")) {
  fail("Card chips must roll the cover to tagged slides");
}
if (!card.includes("displayDescription")) {
  fail("Cards must show the garment description when the catalog has one");
}
if (!card.includes("translate=\"no\"")) {
  fail("Look card names and descriptions must not be auto-translated");
}
if (card.includes("gallery-water-sheen") || card.includes("data-water-roll")) {
  fail("Card color roll must not sheen or water-roll peek chrome");
}
if (card.includes("color-glass-film")) {
  fail("Do not frost per-card — look glass stays content-wide");
}

const gallery = read("components/product-gallery.tsx");
if (!gallery.includes("PhotoLightbox") || !gallery.includes("GalleryPeekRoll")) {
  fail("PDP hero must open the ink/gold lightbox from the peek roll");
}
if (!gallery.includes('data-testid="gallery-color-empty"') || !gallery.includes("emptyGalleryAnnouncement(colorLabel)")) {
  fail("A color with no shots must glass-cover the other finish, not steal its JPEG");
}
if (!gallery.includes("colorHasShots ? () => setLightbox(true)")) {
  fail("Empty-color overlay must not open the lightbox on the other finish");
}
if (!gallery.includes("ky-gallery-frame") || !gallery.includes('data-testid="gallery-frame"')) {
  fail("VT name must sit on the named 3/4 frame, not a remounting color layer");
}
if (!css.includes("@media (max-height: 540px)") || !css.includes("100dvh - 8.75rem")) {
  fail("PDP gallery must cap on short viewports so peek chrome stays on screen");
}
if (!css.includes("@media (max-width: 767px) and (min-height: 541px)") || !css.includes("100dvh - 29rem")) {
  fail("Phone portrait PDP gallery must leave room above the sticky Message bar");
}
if (!gallery.includes("viewTransitionName: `product-${product.ma}`")) {
  fail("PDP hero must use product-{THIS mã} as the view-transition name");
}
if (/className="ky-gallery-set"[\s\S]{0,160}viewTransitionName/.test(gallery)) {
  fail("Do not put view-transition-name on the color-fade set");
}
if (!gallery.includes("imagesForColor") || !gallery.includes("uniqueImageSrcs")) {
  fail("Color pick must keep imagesForColor (tagged ∪ untagged, unique srcs)");
}
if (!gallery.includes("productGalleryReel") || !gallery.includes("clampedReelIndexForColor")) {
  fail("Color tap must roll this mã’s reel to tagged or shared slides");
}
if (gallery.includes("key={colorId") || gallery.includes('key={colorId ?? "all"}') || gallery.includes("colorCrossfade")) {
  fail("Color tap must not remount AnimatePresence on the same JPEG");
}
if (!gallery.includes("useState<string | null>(null)")) {
  fail("Do not auto-select the first hex on load");
}
if (!gallery.includes("current === target ? current : target")) {
  fail("Color tap must roll this mã’s reel by index, not remount a JPEG");
}
if (!gallery.includes("product.colors.length > 0")) {
  fail("PDP chips only when colors[] exist");
}
if (!gallery.includes("product.sizes.length > 0") || !gallery.includes('data-testid="pdp-size-chips"')) {
  fail("PDP size chips only when catalog sizes[] exist");
}
if (!gallery.includes('hairlineLayoutId="pdp-size"')) {
  fail("PDP size chips must use the gold hairline layoutId pdp-size");
}
const look = read("components/product-look.tsx");
if (!look.includes('hairlineLayoutId="pdp-color"') && !gallery.includes('hairlineLayoutId="pdp-color"')) {
  fail("PDP chips must use the gold hairline layoutId pdp-color");
}
if (!look.includes("ContentWaveLooks") || !look.includes("ProductGallery")) {
  fail("PDP glass must sit on the gallery look, not the listing copy");
}
if (!look.includes("hidden md:block") || !look.includes("MessengerCta")) {
  fail("In-column Message must yield to the phone buy bar (desktop keeps the CTA)");
}
if (gallery.includes('mode="wait"') || gallery.includes("x:24")) {
  fail("Color motion must not wait-slide or x:24");
}

const roll = read("components/gallery-peek-roll.tsx");
if (!roll.includes("data-gallery-roll") || !roll.includes("ky-gallery-port") || !roll.includes("pdp-rail")) {
  fail("Gallery must be a native snap port with single/peek marks");
}
if (!roll.includes('"peek"') || !roll.includes('"single"') || !roll.includes("data-count")) {
  fail("One photo stays single — no fake cloned peek");
}
if (
  roll.includes("ky-frost-start") ||
  roll.includes("ky-frost-end") ||
  roll.includes("ky-gallery-edge") ||
  roll.includes("backdrop-filter") ||
  roll.includes("backdropFilter")
) {
  fail("Do not frost neighbor cloth — mask-image on the rail only");
}
if (roll.includes("gallery-water-sheen") || roll.includes("data-water-roll") || roll.includes("pulseWater")) {
  fail("Color roll must not sheen peek chrome");
}
if (css.includes("transparent 16%") && css.includes("transparent 84%") && css.includes("gallery-water-sheen")) {
  fail("Gallery water sheen mask must stay gone");
}
if (!roll.includes("data-edge") || !roll.includes("galleryPeekEdge") || !roll.includes("pdp-slide")) {
  fail("Paper-edge mask must follow the snapped index (start / end / both)");
}
if (roll.includes("viewTransitionName")) {
  fail("VT name belongs on the 3/4 frame, not the remounting roll");
}
if (!roll.includes("useScroll") || !roll.includes("animateGalleryScrollTo") || !roll.includes("galleryScrollBehavior")) {
  fail("Framer useScroll is chrome-only; color/peek roll is viscous RAF, Reduce is instant");
}
if (roll.includes("drag=") || roll.includes("useMotionValue") || roll.includes("springGallery")) {
  fail("Never Motion-drag the snap port");
}
if (roll.includes("gallery-peek-veil") || roll.includes("gallery-frost-edge")) {
  fail("Do not frost the garment — veil/edge-on-img is forbidden");
}
if (image.includes("clipPath") || image.includes("clip-path") || roll.includes("clipPath")) {
  fail("clip-path pour must not sit on garments or gallery photos");
}
if (roll.includes("ky-gold-goo") || image.includes("ky-gold-goo")) {
  fail("Goo must never sit on covers");
}
if (!roll.includes('aria-label="Ảnh trước"') || !roll.includes('aria-label="Ảnh sau"')) {
  fail("Prev/next must be Ảnh trước / Ảnh sau");
}
if (!roll.includes('case "Home"') || !roll.includes('case "End"')) {
  fail("Gallery rail must keep Home / End with the arrow keys");
}
if (!roll.includes('sizes={peeking ? "(min-width: 1024px) 42vw, 100vw"')) {
  fail("Peek photos must declare 100vw sizes on phone; n=1 stays full-bleed");
}
if (!roll.includes("object-top")) {
  fail("PDP peek photos must pin object-top so garments are not cropped at the neck");
}
if (!roll.includes("galleryReelLabel") || !roll.includes("photoPositionLabel")) {
  fail("Gallery region/slide aria must stay bilingual like View larger");
}
if (!roll.includes('aria-haspopup="dialog"') && !roll.includes('aria-haspopup={isCenter')) {
  fail("Center photo must mark the lightbox as a dialog popup");
}
if (!roll.includes("min-w-11") || !roll.includes("touch-manipulation")) {
  fail("Gallery dots and arrows must stay thumb-tall");
}
if (!roll.includes("disabled={!canPrev}") || !roll.includes("disabled={!canNext}")) {
  fail("n>1 prev/next stay visible and disabled at ends — never wrap");
}
if (!css.includes(".liquid-glass") || !css.includes(".ky-gallery-port") || !css.includes(".pdp-rail")) {
  fail("Liquid-glass chrome + snap port must live in CSS");
}
if (!css.includes(".liquid-glass-bar") || !css.includes(".liquid-glass-sheet") || !css.includes(".liquid-glass-caption")) {
  fail("Header/bar, modal sheet, and photo captions must share the glass language");
}
if (!css.includes("--glass-blur: 22px") || !css.includes("--glass-blur-bar: 32px") || !css.includes("--glass-sat: 1.7")) {
  fail("Glass blur tokens must stay see-through (not a paper wash)");
}
if (css.includes("var(--paper) 42%") || css.includes("paper) 42%")) {
  fail("Liquid glass must not be a milky paper mix");
}
if (!css.includes("background: rgb(255 255 255 / 0.48)")) {
  fail("Regular glass bars must be 48% frost for ink contrast, not a 26% wash");
}
if (css.includes("rgb(255 255 255 / 0.26)")) {
  fail("Regular glass bars must not stay at 26% wash");
}
if (css.includes("background: rgb(255 255 255 / 0.38)")) {
  fail("Regular glass bars must not stay at 38% wash");
}
if (!css.includes("rgb(17 17 17 / 0.32)")) {
  fail("Clear glass over photos must stay a dark frost, not milky paper");
}
if (!css.includes("--muted: #2e2e2e")) {
  fail("Regular glass bars must darken muted ink for contrast on frost");
}
if (!css.includes("0 0 12px rgb(255 255 255 / 0.88)")) {
  fail("Regular glass bars must keep an ink halo so type reads over photos");
}
if (!css.includes("0 0 16px rgb(255 255 255 / 0.95)")) {
  fail("Phone buy bar halo must read over dark garment hems without milking the frost");
}
if (!css.includes(".ky-header-film,\n.ky-buy-bar")) {
  fail("Header frost must keep the buy-bar ink halo so category tabs read over photos");
}
if (css.includes("Enter Passcode") || roll.includes("Enter Passcode") || gallery.includes("Enter Passcode")) {
  fail("Passcode screenshot is a material reference only — no lock-screen UI");
}
if (!css.includes(".ky-gallery-controls") || !roll.includes("ky-gallery-controls") || !roll.includes("rounded-2xl")) {
  fail("Gallery prev/next must be edge glass chrome over the photo, not a keypad");
}
if (!css.includes(".ky-gallery-dock") || !roll.includes("ky-gallery-dock")) {
  fail("Gallery dots must stay in the dock");
}
if (!roll.includes("overflow-x-auto tab-scroll") || !roll.includes("w-max max-w-full")) {
  fail("Gallery dots must scroll inside the glass capsule");
}
if (roll.includes("Enter Passcode") || roll.includes("Emergency") && roll.includes("Cancel")) {
  fail("Do not ship an iOS lock-screen keypad");
}
if (roll.includes("absolute left-2") || roll.includes("-translate-y-1/2")) {
  fail("Gallery arrows use the edge glass row, not a centered keypad stack");
}
if (css.includes("grid-auto-columns: 78%") || css.includes("scroll-padding-inline: 11%")) {
  fail("PDP rail must not keep 78% / 11% neighbor peeks");
}
if (css.includes("ky-frost-start") || css.includes("ky-frost-end") || css.includes(".ky-gallery-edge")) {
  fail("Frost strips must not sit on peek cloth");
}
if (!css.includes("prefers-reduced-transparency")) {
  fail("Reduced transparency must kill glass films");
}
const reduceTransparencyCss = css.split("@media (prefers-reduced-transparency: reduce)")[1] ?? "";
if (
  !reduceTransparencyCss.includes(".liquid-glass") ||
  !reduceTransparencyCss.includes(".liquid-glass-bar") ||
  !reduceTransparencyCss.includes(".ky-chrome-blur") ||
  !reduceTransparencyCss.includes(".pdp-lightbox-veil") ||
  !reduceTransparencyCss.includes(".ky-buy-bar")
) {
  fail("Reduced transparency must kill liquid-glass, buy-bar blur, and lightbox veil");
}
if (!css.includes("@media print") || !css.includes("[data-testid=\"shop-ship-bar\"]")) {
  fail("Print must hide the phone buy bar and sticky chrome");
}
if (!css.includes("[data-testid=\"shop-message-cta\"]") || !css.includes("[data-testid=\"shop-ask-price\"]")) {
  fail("Print must hide Message CTAs");
}
if (!css.includes("[data-testid=\"card-cover-reel\"]") || !css.includes("break-inside: avoid")) {
  fail("Print must keep look covers on one page");
}
if (!css.includes("forced-colors: active") || !css.includes("prefers-contrast: more")) {
  fail("Forced colors and more-contrast must keep gold hairlines visible");
}
const moreContrastCss = css.split("@media (prefers-contrast: more)")[1] ?? "";
if (!moreContrastCss.includes(".liquid-glass") || !moreContrastCss.includes(".ky-chrome-blur") || !moreContrastCss.includes(".liquid-glass-bar") || !moreContrastCss.includes(".ky-buy-bar")) {
  fail("More-contrast must deepen liquid-glass and the phone buy-bar rim");
}
if (!(moreContrastCss.split("rgb(255 255 255 / 0.92)")[0] ?? "").includes(".liquid-glass-sheet")) {
  fail("More-contrast must deepen modal sheets with Regular bars");
}
if (!(moreContrastCss.split("rgb(255 255 255 / 0.92)")[0] ?? "").includes(".liquid-glass-chip")) {
  fail("More-contrast must deepen glass chips with Regular bars");
}
if (!css.split("@media (prefers-contrast: more)")[1]?.includes("--muted:")) {
  fail("More-contrast must deepen muted copy");
}
if (!css.includes("--fade: 1.25rem") || !css.includes("--blur-md: 12px")) {
  fail("Paper-edge fade and chrome blur tokens must stay");
}
if (
  !css.includes('[data-edge="start"]') ||
  !css.includes('[data-edge="end"]') ||
  !css.includes('[data-edge="both"]')
) {
  fail("Mask must be directional (start / end / both)");
}
if (!css.includes("scroll-snap-type: x mandatory") || !css.includes("mask-image")) {
  fail("Port must snap and mask edges into paper");
}
if (!css.includes('data-gallery-roll="single"') || !css.includes("grid-auto-columns: 100%")) {
  fail("n=1 must be a full-bleed snap child, not a fake 78% peek");
}
if (css.includes("scroll-snap-type: none")) {
  fail("Reduce Motion must keep UA snap; only mask and veil blur go");
}
if (!css.includes("mask-image: none") || !css.includes(".pdp-lightbox-veil")) {
  fail("Reduce Motion must kill the edge mask; lightbox veil class must exist");
}
if (css.includes("transition: mask") || css.includes("animation: mask")) {
  fail("Do not animate the paper-edge mask");
}
if (css.includes(".gallery-water-sheen")) {
  fail("Gallery sheen class must stay gone");
}

const lightbox = read("components/photo-lightbox.tsx");
if (!lightbox.includes("createPortal") || !lightbox.includes("bg-ink/70")) {
  fail("Lightbox must portal with an ink veil (not intake rose)");
}
if (lightbox.includes("rgba(17,17,17,0.45)")) {
  fail("Lightbox sheet must not drop a 45% ink shadow");
}
if (!lightbox.includes("rgba(17,17,17,0.28)")) {
  fail("Lightbox sheet must stay a quiet ink veil");
}
if (!lightbox.includes("pdp-lightbox-veil") || !lightbox.includes("pdp-lightbox-rail")) {
  fail("Lightbox must use the chrome veil + same-mã snap rail");
}
if (!lightbox.includes("liquid-glass-sheet") || !lightbox.includes("ky-gallery-controls")) {
  fail("Lightbox sheet must be frosted glass; arrows sit over the photo");
}
if (!lightbox.includes("liquid-glass-chip")) {
  fail("Lightbox close and dots must stay boutique glass, not a keypad");
}
if (!lightbox.includes("z-[80]")) {
  fail("Lightbox must sit above the sticky Message bar");
}
if (!lightbox.includes("disabled={!canPrev}") || !lightbox.includes("disabled={!canNext}")) {
  fail("Lightbox arrows stay visible and disabled at ends — never wrap");
}
if (!lightbox.includes("clampGalleryIndex") || lightbox.includes("% slides.length")) {
  fail("Lightbox arrows/swipe must clamp at ends — never wrap");
}
if (!lightbox.includes('aria-label="Đóng"') || !lightbox.includes("h-11 w-11")) {
  fail("Lightbox close must be 44×44 with Đóng");
}
if (!lightbox.includes("safe-area-inset-top")) {
  fail("Lightbox must pad the notch");
}
if (lightbox.includes("rose") || lightbox.includes("001.jpg") || lightbox.includes("002.jpg")) {
  fail("Lightbox must not import intake rose or invent 001.jpg");
}

const buyBar = read("components/buy-bar.tsx");
if (!buyBar.includes("liquid-glass-bar") || !buyBar.includes("ky-chrome-blur") || !buyBar.includes("border-gold/45")) {
  fail("Phone bar must be frosted glass + gold/45, not milky paper/95");
}
if (buyBar.includes("bg-paper/95")) {
  fail("Phone bar must not use milky paper/95 over the look");
}
if (!buyBar.includes("ky-chrome-blur")) {
  fail("Phone bar must keep a chrome-blur class so Reduced Transparency can kill it");
}
if (buyBar.includes("truncate") || buyBar.includes("text-base font-medium")) {
  fail("Phone bar must not truncate Inbox for price; price stays 13px KY");
}
if (!buyBar.includes("text-[13px]")) {
  fail("Phone buy bar price must stay 13px KY");
}
if (!buyBar.includes("ky-buy-bar") || !css.includes(".ky-buy-bar")) {
  fail("Phone buy bar must keep a stronger ink halo over dark hems");
}
if (!css.includes("0 0 16px rgb(255 255 255 / 0.95)")) {
  fail("Phone buy bar halo must read over dark garment hems without milking the frost");
}
if (
  !css.includes('.ky-buy-bar [data-testid="shop-message-cta"]') ||
  !css.includes('.ky-buy-bar [data-testid="shop-ask-price"]') ||
  !css.includes("0 0 0 1px rgb(255 255 255 / 0.55)")
) {
  fail("Phone buy-bar Message must keep a quiet paper hairline over dark hems");
}
if (!buyBar.includes("whitespace-nowrap")) {
  fail("Phone Message must not wrap on the buy bar");
}
if (!buyBar.includes("displayName") || !buyBar.includes("line-clamp-2")) {
  fail("Phone buy bar must show the look name after the title scrolls away");
}
if (!buyBar.includes("<MaMark") || !buyBar.includes("text-[10px] tracking-[0.16em] text-muted")) {
  fail("Phone buy bar must keep mã as a quiet kicker beside the look name");
}
if (!buyBar.includes("select-none") || !buyBar.includes("overscroll-contain")) {
  fail("Phone buy bar name must not select on tap; overscroll must stay in the bar");
}
if (!buyBar.includes('translate="no"')) {
  fail("Phone buy bar look names and prices must not be auto-translated");
}
if (!buyBar.includes('role="region"')) {
  fail("Phone buy bar must be a named region for the look");
}
if (!buyBar.includes("safe-area-inset-left") || !buyBar.includes("safe-area-inset-right")) {
  fail("Phone buy bar must pad landscape home indicators");
}

const featured = read("components/featured-board.tsx");
if (!featured.includes("ArrowRight") || !featured.includes("ArrowLeft") || !featured.includes("Home")) {
  fail("Featured tabs must keep APG keyboard");
}
if (!featured.includes('role="tablist"') || !featured.includes("aria-controls") || !featured.includes('role="tabpanel"')) {
  fail("Featured tabs must stay a tablist with a tabpanel");
}
if (!featured.includes('aria-orientation="horizontal"')) {
  fail("Featured tablist must stay a horizontal APG tablist");
}
if (!featured.includes("aria-posinset") || !featured.includes("aria-setsize")) {
  fail("Featured tabs must keep APG posinset");
}
if (featured.includes('aria-roledescription="carousel"')) {
  fail("FeaturedBoard must not be marked a carousel");
}
if (!featured.includes("product.type === filter")) {
  fail("Featured filter must keep Holds in the right category (type, not status)");
}
if (!featured.includes("opacity: 1, y: 0, transition: { duration: 0 }")) {
  fail("Featured look count must not bounce when Reduce Motion is on");
}
if (featured.includes("y: 4") || featured.includes("y: -4")) {
  fail("Look count must fade, not bounce");
}

const grid = read("components/animated-product-grid.tsx");
if (!grid.includes("filterSlide") || !grid.includes("data-filter-ms") || !grid.includes("FILTER_SLIDE_SECONDS") || !grid.includes("data-filter-slide")) {
  fail("Featured filter motion must be the quiet 280ms opacity slide");
}
if (!grid.includes("featured-pour") || !grid.includes('mode="sync"') || !grid.includes("featured-pour-stack")) {
  fail("Featured looks must overlap (sync) in a stacked cell");
}
if (grid.includes("featured-pour-wash") || card.includes("color-glass-film")) {
  fail("Do not frost per-tab or per-card");
}
const waveFx = read("components/content-wave.tsx");
if (waveFx.includes('data-wave-glass="water"') || waveFx.includes("WaveRibbon") || waveFx.includes("content-wave-sheet")) {
  fail("Looks host must not paint a watery glass ribbon");
}
if (waveFx.includes("GlassHeart") || waveFx.includes('data-wave-glass="hearts"') || waveFx.includes("contentWaveHearts")) {
  fail("Looks host must not paint a heart curtain");
}
if (!waveFx.includes("IntersectionObserver") || !waveFx.includes("play()")) {
  fail("Content wave must one-shot when the looks stage is on screen, then still");
}
if (waveFx.includes("{ threshold: 0 }")) {
  fail("Intro sheen must wait until looks are on screen, not fire under the hero");
}
if (!waveFx.includes('data-wave-glass="sheen"') || !waveFx.includes('data-testid="content-wave-sheen"') || !waveFx.includes("content-wave-sheen")) {
  fail("Looks host must paint a one-shot soft sheen");
}
if (!waveFx.includes("ContentWaveLooks") || !waveFx.includes('data-testid="content-wave-looks"')) {
  fail("Looks stages must keep the content wrapper, not wrap the hero or tab chrome");
}
if (waveFx.includes("content-wave-echo") || waveFx.includes("content-wave-ripple")) {
  fail("Looks host must not trail an echo/ripple meniscus");
}
if (!featured.includes("useContentWave") || !featured.includes("wave.play")) {
  fail("Featured tab switch must play the soft sheen");
}
if (CONTENT_WAVE_MS < 1000 || CONTENT_WAVE_MS > 1400) {
  fail("Sheen travel must stay slow (~1s–1.4s)");
}
if (contentWaveDurationMs() < 1000 || contentWaveDurationMs() > 1400) {
  fail("Sheen must unmount after a slow ~1s+ sweep (within 1.4s)");
}
if (CONTENT_WAVE_HOLD_MS < 40 || CONTENT_WAVE_HOLD_MS > 160) {
  fail("Sheen must settle briefly, then unmount");
}
if (CONTENT_WAVE_INTRO_RATIO < 0.08 || CONTENT_WAVE_INTRO_RATIO > 0.2) {
  fail("Intro sheen must wait for looks on screen, not the hero peek");
}
if (!featured.includes("ContentWaveLooks") || !featured.includes("featured-panel")) {
  fail("Featured looks must sit on the looks grid, not the filter tabs");
}
if (featured.includes("aria-busy")) {
  fail("Featured panel must not mark a watery pour as busy");
}
if (!featured.includes('data-testid="looks-heading"')) {
  fail("Featured board must keep the Looks editorial heading");
}
if (!featured.includes("tabIndex={-1}") || !featured.includes("outline-none")) {
  fail("Looks heading must receive skip-to-looks focus without a page-sized ring");
}
if (!featured.includes('translate="no"')) {
  fail("Looks heading and filter names must not be auto-translated");
}
const chipsShop = read("components/color-name-chips.tsx");
if (!chipsShop.includes("useContentWave") || !chipsShop.includes("wave.play")) {
  fail("Color switch must play the soft sheen");
}
if (!chipsShop.includes("min-h-8")) {
  fail("Card color chips must stay thumb-tall (min-h-8)");
}
if (!chipsShop.includes("COLOR_FIELD_LEGEND") || !chipsShop.includes("tracking-[0.16em]")) {
  fail("PDP color chips must match the Màu / Color legend tracking");
}
const loading = read("app/(shop)/(browse)/loading.tsx");
if (!loading.includes("gap-x-3 gap-y-12") || !loading.includes("Looks")) {
  fail("Loading skeleton must match the Looks grid rhythm");
}
if (!read("components/product-grid.tsx").includes("gap-x-3 gap-y-12")) {
  fail("Looks grid must share the loading skeleton rhythm");
}
if (!loading.includes("min-w-0")) {
  fail("Loading skeleton must match the Looks grid shrink");
}
if (!loading.includes("Đang tải · Loading")) {
  fail("Loading kicker must stay bilingual like gallery photo labels");
}
if (!loading.includes("liquid-glass-chip")) {
  fail("Loading kicker must sit on Regular glass");
}
if (!loading.includes("min-h-11")) {
  fail("Loading kicker chip must stay thumb-tall");
}
if (!loading.includes("select-none")) {
  fail("Loading kicker must not select on tap");
}
if (!loading.includes("whitespace-nowrap") || !loading.includes("truncate")) {
  fail("Loading kicker must stay one KY line");
}
if (!loading.includes("outline-none")) {
  fail("Loading Looks heading must not show a page-sized gold ring");
}
if (!loading.includes('role="status"') || !loading.includes("aria-hidden")) {
  fail("Loading must be a status; skeleton tiles stay decorative");
}
if (!loading.includes("aria-atomic")) {
  fail("Loading must announce the whole bilingual kicker");
}
const announce = read("components/announcement-bar.tsx");
if (!announce.includes("safe-area-inset-top") || !announce.includes("prefers-reduced-motion: reduce")) {
  fail("Announcement must pad the notch and stop rotating under Reduce Motion");
}
if (!announce.includes("safe-area-inset-left") || !announce.includes("safe-area-inset-right")) {
  fail("Announcement must pad landscape home indicators");
}
if (!announce.includes("text-[11px]") || !announce.includes("tracking-[0.18em]")) {
  fail("Announcement kicker must stay 11px KY tracking");
}
if (!announce.includes("whitespace-nowrap")) {
  fail("Announcement must stay one KY line (no wrap in the ink bar)");
}
if (!announce.includes("overflow-x-auto tab-scroll")) {
  fail("Announcement must scroll a long KY line instead of clipping it");
}
if (!announce.includes("min-w-0 max-w-full")) {
  fail("Announcement rail must shrink instead of blowing the chrome");
}
if (!announce.includes("aria-live") || !announce.includes("select-none")) {
  fail("Announcement must announce line changes and stay unselectable");
}
if (!announce.includes('translate="no"')) {
  fail("Announcement copy must not be auto-translated");
}
if (!announce.includes("visibilitychange") || !announce.includes("document.hidden")) {
  fail("Announcement must pause when the tab is hidden");
}
if (!announce.includes("paused") || !announce.includes("(hover: hover)")) {
  fail("Announcement must pause on hover pointers so the line can be read");
}
const rootLayout = read("app/layout.tsx");
if (!rootLayout.includes('themeColor: "#111111"') || !rootLayout.includes("viewportFit: \"cover\"")) {
  fail("iOS theme-color must match the sticky ink ticker");
}
if (!rootLayout.includes('colorScheme: "light"')) {
  fail("Viewport color-scheme must stay light with the paper shop");
}
if (rootLayout.includes("https://m.me") || rootLayout.includes("dns-prefetch") || rootLayout.includes("preconnect")) {
  fail("Root layout must not prefetch m.me — that makes iPhone open Safari/Facebook profile instead of the Messenger inbox");
}
if (!rootLayout.includes("min-h-dvh")) {
  fail("Root must fill the dynamic iOS viewport");
}
if (!css.includes("-webkit-touch-callout: none") || !css.includes(".ky-gallery-shell img") || !css.includes(".ky-collection-rail img")) {
  fail("Gallery photos must not show the iOS callout sheet");
}
if (!css.includes(".ky-thumb-rail img") || !css.includes(".pdp-lightbox-rail img")) {
  fail("Thumb and lightbox photos must not show the iOS callout sheet");
}
if (!css.includes("-webkit-user-drag: none")) {
  fail("Garment photos must not drag off the lookbook on iOS");
}
if (!css.includes(".liquid-glass:hover:not(:disabled)")) {
  fail("Gallery glass chrome must gold-up on hover pointers only");
}
if (!css.includes("scroll-padding-inline: 0.5rem")) {
  fail("Thumb rails must keep a little scroll padding so the last thumb is not flush");
}
const adminEntry = read("components/admin-entry.tsx");
if (!adminEntry.includes("liquid-glass-sheet") || !adminEntry.includes("pdp-lightbox-veil")) {
  fail("Shop tools sheet must be frosted glass over a veiled shop");
}
if (adminEntry.includes("shadow-xl") || adminEntry.includes("rgba(17,17,17,0.45)")) {
  fail("Shop tools sheet must not use a cheap drop shadow");
}
if (!adminEntry.includes("rgba(17,17,17,0.28)")) {
  fail("Shop tools sheet must stay a quiet ink veil");
}
if (!adminEntry.includes("leading-[1.08]") || !adminEntry.includes("min-h-11 touch-manipulation")) {
  fail("Shop tools gate must stay thumb-tall with unclipped serif");
}
if (!adminEntry.includes("whitespace-nowrap")) {
  fail("Shop tools Open admin / Close must stay one KY line");
}
if (!adminEntry.includes("liquid-glass-chip") || !adminEntry.includes("Close")) {
  fail("Shop tools Close must be a glass chip, not muted text");
}
if (!adminEntry.includes("safe-area-inset-right")) {
  fail("Shop tools dot must clear the landscape home indicator");
}
if (!adminEntry.includes("safe-area-inset-left")) {
  fail("Shop tools gate must pad landscape home indicators");
}
if (!adminEntry.includes("Công cụ shop · Shop tools") || !adminEntry.includes('aria-label="Đóng"')) {
  fail("Shop tools aria must stay bilingual; overlay close matches lightbox Đóng");
}
if (!adminEntry.includes('aria-haspopup="dialog"') || !adminEntry.includes("aria-expanded")) {
  fail("Shop tools dot must mark the overlay as a dialog");
}
if (!adminEntry.includes('case "Tab"') || !adminEntry.includes("safe-area-inset-bottom")) {
  fail("Shop tools gate must trap Tab and pad the home indicator");
}
if (!adminEntry.includes("overscroll-contain")) {
  fail("Shop tools overlay must contain overscroll like the lightbox");
}
if (!adminEntry.includes("inert = true")) {
  fail("Shop tools overlay must inert the shop behind the dialog");
}
if (!adminEntry.includes('data-testid="skip-to-looks"')) {
  fail("Shop tools overlay must inert the skip link");
}
if (!adminEntry.includes('document.body.style.overflow = "hidden"') || !adminEntry.includes("previousFocus")) {
  fail("Shop tools overlay must lock page scroll and restore focus like the lightbox");
}
if (!adminEntry.includes("document.documentElement.style.overflow") || !adminEntry.includes("tabIndex={-1}")) {
  fail("Shop tools overlay must lock html scroll and keep the veil out of the tab cycle");
}
if (!adminEntry.includes("aria-hidden")) {
  fail("Shop tools gold pill must stay decorative inside the labeled button");
}
if (!adminEntry.includes("hover-hover:hover:opacity-90")) {
  fail("Open admin must dim on hover pointers");
}
if (look.includes("showChips={false}")) {
  fail("PDP color chips must sit under the gallery thumbs, not be hidden from the photos");
}
if (!gallery.includes('data-testid="pdp-color-chips"')) {
  fail("Màu / Color chips must sit on the gallery, just below the pictures");
}
if (!gallery.includes("mb-2 max-w-full truncate whitespace-nowrap")) {
  fail("Màu / Color legend must stay one KY line");
}
if (!chipsShop.includes("ky-color-chip") || !css.includes(".ky-color-chip") || !chipsShop.includes("liquid-glass-chip")) {
  fail("Color names must sit in a visible glass box");
}
if (!css.includes('.ky-color-chip[aria-checked="true"]')) {
  fail("Selected color box must be obvious vs unselected");
}
if (!chipsShop.includes("min-h-11") || !chipsShop.includes("min-h-8")) {
  fail("PDP color chips must be 44px; card chips stay compact min-h-8");
}
if (!chipsShop.includes("whitespace-nowrap")) {
  fail("Color names must stay one KY line");
}
if (!chipsShop.includes("aria-hidden")) {
  fail("Color gold hairlines must stay decorative");
}
if (!chipsShop.includes('aria-orientation="horizontal"')) {
  fail("Color chips must stay a horizontal radiogroup");
}
if (!chipsShop.includes("aria-describedby") || !chipsShop.includes("aria-posinset")) {
  fail("Color chips must name set size and point at the color note");
}
if (!chipsShop.includes('translate="no"')) {
  fail("Color names must not be auto-translated");
}
if (!chipsShop.includes("select-none")) {
  fail("Color names must not select on tap");
}
if (!chipsShop.includes("flex-nowrap") || !chipsShop.includes("overflow-x-auto tab-scroll")) {
  fail("Color chips must stay a one-row tab-scroll rail");
}
if (!chipsShop.includes("scrollChromeChildIntoView") || !chipsShop.includes('[aria-checked="true"]')) {
  fail("Color chips must keep the selected name in the rail via scrollLeft");
}
if (chipsShop.includes(".scrollIntoView")) {
  fail("Color chips must not use page scrollIntoView");
}
if (chipsShop.includes("flex flex-wrap")) {
  fail("Color chips must not wrap under the look");
}
if (!chipsShop.includes("shrink-0")) {
  fail("Color chips must not shrink in the rail");
}
if (!chipsShop.includes("useLayoutEffect") || !chipsShop.includes("railRef")) {
  fail("Color chips must snap the selected name after layout");
}
if (!chipsShop.includes("scroll-px-2")) {
  fail("Color chip rail must keep a little scroll padding so the last name is not flush");
}
if (!chipsShop.includes("min-w-0 max-w-full")) {
  fail("Color chip rail must shrink inside look cards instead of blowing the grid");
}
if (!loading.includes("shimmer") || !loading.includes("aspect-[3/4]")) {
  fail("Loading tiles must keep the 3/4 paper well and one-shot shimmer");
}
if (!loading.includes("liquid-glass-rim") || !loading.includes("bg-gold/45")) {
  fail("Loading tiles must preview look-card glass rim and gold hairline");
}
const home = read("app/(shop)/(browse)/page.tsx");
const heroAt = home.indexOf("<HeroEditorial");
const waveAt = home.indexOf("<ContentWaveHost");
if (heroAt < 0 || waveAt < 0 || heroAt > waveAt) {
  fail("Shop content must sit below the hero");
}
if (home.includes("CollectionList") || home.includes("ky-collection-rail")) {
  fail("Home must not render the under-hero collection tab rail");
}
const motionHelpers = read("lib/motion.ts");
if (motionHelpers.includes("clipPath") || motionHelpers.includes("inset(0 0 0 28% round")) {
  fail("filterSlide must not watery-pour with a clip-path");
}
if (motionHelpers.includes("x: 28 *") || motionHelpers.includes("x: 14 *") || motionHelpers.includes("duration: 0.54") || motionHelpers.includes("540ms")) {
  fail("filterSlide must not keep the 540ms wait / page-flip x");
}
if (!motionHelpers.includes("x: 12 *") || !motionHelpers.includes("x: -8 *")) {
  fail("Looks slide x must stay small (12 / -8)");
}
const slideBody = motionHelpers.split("export function filterSlide")[1]?.split("export function colorCrossfade")[0] ?? "";
if (slideBody.includes("springSoft") || slideBody.includes('type: "spring"')) {
  fail("Do not spring the looks crossfade — tween opacity and x");
}
if (!slideBody.includes("opacity: 0") || !slideBody.includes("opacity: 1")) {
  fail("filterSlide must crossfade opacity");
}
if (motionHelpers.includes("GALLERY_SLIDE_RATIO = 0.78") || motionHelpers.includes("GALLERY_GAP_PX = 12")) {
  fail("Peek gutters must not return — 78% / 12px ate the product on phone");
}
if (!motionHelpers.includes("GALLERY_SLIDE_RATIO = 1") || !motionHelpers.includes("GALLERY_GAP_PX = 0")) {
  fail("PDP gallery must stay full-bleed (100% / 0 gap)");
}
if (motionHelpers.includes("soft-light")) {
  fail("filterSlide must not soft-light paper onto clothes");
}
if (!featured.includes("scrollChromeChildIntoView") || !featured.includes("slideDirection")) {
  fail("Featured tabs must roll with direction + rail scrollLeft (no page yank)");
}
if (!featured.includes("tabRailRef")) {
  fail("Featured tabs must scroll the tab rail, not the page");
}
if (featured.includes("scrollIntoView")) {
  fail("Featured tabs must not use page scrollIntoView");
}
if (!featured.includes("lookCountLabel") || featured.includes("scaleX: [1, 1.15, 1]")) {
  fail("Featured tabs must keep looks counts without gold meniscus overshoot");
}
if (!featured.includes("liquid-glass-chip") || !featured.includes("featured-tab-film")) {
  fail("Featured selected tab must sit on a glass chip with the gold film");
}
if (!featured.includes("ShopEmpty") || !featured.includes("collectionEmptyCopy")) {
  fail("Featured empty tabs must use the same empty well as collections");
}
if (featured.includes("featured-tab-trail") || featured.includes("ky-gold-goo") || featured.includes("KyGoldGoo")) {
  fail("Gold film must not trail or goo");
}
if (featured.includes("feGaussianBlur") || featured.includes("feColorMatrix") || featured.includes("colorInterpolationFilters")) {
  fail("Gold goo SVG must stay gone");
}
if (featured.includes("feDisplacementMap") || featured.includes("feTurbulence")) {
  fail("Featured chrome must never use displacement");
}

const cta = read("components/messenger-cta.tsx");
const header = read("components/header.tsx");
if (!cta.includes("ky-chrome-rim")) {
  fail("Message CTA must carry a 1–1.5px chrome rim");
}
if (cta.includes("cta-shine") || cta.includes("scale: 1.04")) {
  fail("Message CTA must not flash or scale-pop");
}
if (cta.includes("rgba(17,17,17,0.5)")) {
  fail("Primary Message hover shadow must stay quiet, not a 50% ink drop");
}
if (!cta.includes("rgba(17,17,17,0.28)")) {
  fail("Primary Message hover shadow must stay a quiet ink veil");
}
if (!cta.includes("min-h-11") || !cta.includes("touch-manipulation")) {
  fail("Message CTAs must stay thumb-tall");
}
if (!cta.includes("messageAria")) {
  fail("Message CTA aria must stay bilingual");
}
if (!cta.includes("w-full bg-gold/45")) {
  fail("Header and card Message gold is always-on on touch");
}
if (!cta.includes('tracking-[0.18em] text-ink hover-hover:hover:text-gold-deep')) {
  fail("Header Message must gold-up on hover pointers");
}
if (!cta.includes("border-gold/45")) {
  fail("Footer ghost Message must keep a quiet gold rim on touch");
}
if (cta.includes("group-hover/cta:w-full")) {
  fail("Card Message gold must not be hover-only");
}
if (!cta.includes("motion-safe:hover-hover:group-hover/cta:translate-x-0.5")) {
  fail("Message arrow must be motion-safe and hover-only");
}
if (!cta.includes("useCanHover")) {
  fail("Message lift must not run on touch pointers");
}
if (!cta.includes('translate="no"')) {
  fail("Message chrome must not be auto-translated");
}
if (!cta.includes('referrerPolicy="no-referrer"')) {
  fail("Message must not send a referrer into Messenger");
}
if (cta.includes('target="_blank"') || cta.includes("noopener noreferrer")) {
  fail("Message CTAs must not force a Safari blank tab");
}
if (cta.includes("openMessengerChat") || cta.includes("onClick") || cta.includes("setTimeout") || cta.includes("preventDefault")) {
  fail("Message CTAs must not hijack click or delay a web hop — phone uses a native app-scheme <a href>");
}
if (cta.includes("motion.a") || cta.includes("whileTap") || cta.includes("whileHover")) {
  fail("Message must stay a native <a href> — Framer tap/hover on the link blocks the Messenger app");
}
const messengerLib = read("lib/messenger.ts");
if (messengerLib.includes("event.preventDefault") || messengerLib.includes("openMessengerChat") || messengerLib.includes("setTimeout")) {
  fail("Messenger must not delay or hijack taps into a web hop");
}
if (!messengerLib.includes("https://m.me/") || !messengerLib.includes("fb-messenger://user-thread/")) {
  fail("Desktop Message stays https://m.me/{pageId}; phone Message is fb-messenger://user-thread/{pageId}");
}
if (!cta.includes("messengerTapHref") || !cta.includes("messengerHref(facebookPageUrl)")) {
  fail("Phone taps the app scheme; Open on web stays https://m.me");
}
if (!cta.includes("Open on web") || !cta.includes('data-testid="shop-message-web"')) {
  fail("Phone Message must offer a separate Open on web m.me control — not a timer");
}
if (!cta.includes("select-none")) {
  fail("Message chrome must not select on tap");
}
if (!cta.includes("whitespace-nowrap")) {
  fail("Message chrome must stay one KY line");
}
const copyMa = read("components/copy-ma.tsx");
if (!copyMa.includes("min-h-11") || !copyMa.includes("aria-live") || !copyMa.includes("tracking-[0.16em]")) {
  fail("Copy mã must stay thumb-tall with a live copied state");
}
if (!copyMa.includes("border-gold text-ink") || !copyMa.includes("copyMaLabel")) {
  fail("Copied mã must show the gold confirm rim; copy aria stays bilingual");
}
if (!copyMa.includes("liquid-glass-chip")) {
  fail("Copy mã must be a boutique glass chip, not a keypad disc");
}
if (!copyMa.includes("copyMaDoneAria")) {
  fail("Copied mã aria must stay bilingual");
}
if (!copyMa.includes("aria-atomic")) {
  fail("Copied mã live region must announce the whole phrase");
}
if (!copyMa.includes('translate="no"')) {
  fail("Copy mã must not be auto-translated");
}
if (!copyMa.includes("select-none")) {
  fail("Copy mã must not select the button label on tap");
}
if (!copyMa.includes("whitespace-nowrap")) {
  fail("Copy mã must stay one KY line in the breadcrumb rail");
}
if (!copyMa.includes("shrink-0")) {
  fail("Copy mã must not shrink in the PDP breadcrumb rail");
}
if (!copyMa.includes("clearTimeout") || !copyMa.includes("copiedTimer")) {
  fail("Copy mã must clear the copied timer on unmount");
}
if (!look.includes("min-h-11")) {
  fail("PDP breadcrumb category must stay 44px");
}
if (!look.includes("whitespace-nowrap")) {
  fail("PDP breadcrumb category must stay one KY line");
}
if (!look.includes("select-none")) {
  fail("PDP breadcrumb category must not select on tap");
}
if (!look.includes("flex-nowrap") || !look.includes("overflow-x-auto tab-scroll")) {
  fail("PDP breadcrumb must stay a one-row tab-scroll rail");
}
if (!look.includes("flex min-w-0 flex-nowrap items-center gap-x-2 overflow-x-auto tab-scroll")) {
  fail("PDP breadcrumb rail must shrink inside the look column instead of blowing the grid");
}
if (look.includes("flex flex-wrap")) {
  fail("PDP breadcrumb must not wrap Copy mã under the category");
}
if (!look.includes("shrink-0")) {
  fail("PDP breadcrumb category and slash must not shrink in the rail");
}
if (!look.includes("min-w-0")) {
  fail("PDP copy column must shrink so serif names do not overflow the grid");
}
if (!look.includes("categoryAriaLabel")) {
  fail("PDP breadcrumb category must keep recorded VN · EN aria");
}
if (!gallery.includes("text-pretty")) {
  fail("Color notes must wrap pretty");
}
if (!gallery.includes("-color-note")) {
  fail("Color notes must be labelled for the chip radiogroup");
}
const desc = read("components/product-description.tsx");
if (!desc.includes('lang="vi"') || !desc.includes("text-pretty")) {
  fail("VN flavor must be marked lang=vi; description wraps pretty");
}
if (!desc.includes("ky-split-hairline") || !desc.includes("text-ink")) {
  fail("Look copy must sit under a gold hairline; English stays ink, flavor stays muted");
}
if (!desc.includes("[orphans:2]") || !desc.includes("[widows:2]")) {
  fail("Look descriptions must not leave a lone line in print");
}
if (!desc.includes('translate="no"')) {
  fail("Recorded look copy must not be auto-translated");
}
if (!gallery.includes('data-testid="viewing-color" lang="vi"')) {
  fail("Viewing-color live region must stay marked Vietnamese");
}
const hero = read("components/hero-mesh.tsx");
if (!hero.includes("tracking-[0.18em]") || hero.includes("tracking-[0.32em]")) {
  fail("Hero wordmark tracking must stay KY-quiet (0.18em)");
}
if (!hero.includes("select-none") || !hero.includes("text-balance")) {
  fail("Hero kicker must stay unselectable and balance wrap");
}
if (!hero.includes("max-w-full")) {
  fail("Hero kicker must not overflow the gutter");
}
if (!hero.includes("whitespace-nowrap") || !hero.includes("truncate")) {
  fail("Hero kicker must stay one KY line");
}
if (!hero.includes("liquid-glass-caption") || !hero.includes("draggable={false}")) {
  fail("Hero kicker must be glass over the photo; hero must not drag");
}
if (!hero.includes('sizes="50vw"')) {
  fail("Hero panels must declare half-viewport sizes");
}
if (!hero.includes("width={1945}") || !hero.includes("height={3890}")) {
  fail("Hero panels must declare each D02 half JPEG intrinsic size");
}
if (!hero.includes("/editorial/hero-front.jpg") || !hero.includes("/editorial/hero-back.jpg")) {
  fail("Hero must show the D02 front and back panels together");
}
if (!hero.includes("grid-cols-2")) {
  fail("Hero must be two equal columns so front and back both show");
}
const heroBytes = readFileSync(path.join(process.cwd(), "public/editorial/hero.jpg"));
const heroSha = createHash("sha256").update(heroBytes).digest("hex");
if (heroSha !== "0b3c8e94a2f49434a750fc1f719f1275e2e8ae762dc2fafa376815d2637d5d2a") {
  fail("Hero source must stay the full D02 front+back diptych");
}
if (heroBytes.length !== 394355) {
  fail("Hero byte size must match D02-hero.jpg");
}
const heroFrontBytes = readFileSync(path.join(process.cwd(), "public/editorial/hero-front.jpg"));
const heroBackBytes = readFileSync(path.join(process.cwd(), "public/editorial/hero-back.jpg"));
if (createHash("sha256").update(heroFrontBytes).digest("hex") !== "109cc69e4d775bc0d5742f08414e96aa6336d0f71bc8524191b71152897fa137") {
  fail("Hero front panel must stay the left half of the D02 diptych");
}
if (createHash("sha256").update(heroBackBytes).digest("hex") !== "e04d8aeeeed1fcefc2165f9ba8bcc869fc6659f25d31f4a410d92e2867ff71a3") {
  fail("Hero back panel must stay the right half of the D02 diptych");
}
if (!hero.includes('alt=""')) {
  fail("Hero photo must stay decorative under the Sassy Closet kicker");
}
if (!hero.includes('translate="no"')) {
  fail("Hero kicker must not be auto-translated");
}
if (!hero.includes("h-[calc(100svh-8.75rem)]") || !hero.includes("max-w-[min(100%,calc(100svh-8.75rem))]")) {
  fail("Hero must fill the first screen under sticky chrome without cropping a single wide diptych");
}
if (!hero.includes("gap-3") || !hero.includes("sm:gap-5")) {
  fail("Hero front and back must sit apart on paper, not flush");
}
if (!hero.includes("object-contain") || !hero.includes("object-center") || hero.includes("object-cover") || hero.includes("object-top") || hero.includes("object-left") || hero.includes("object-[center_35%]")) {
  fail("D02 hero must contain each front/back panel on paper so the full dress and shoes stay in frame");
}
if (!hero.includes("bg-paper")) {
  fail("Hero letterbox and the gap between panels must be warm paper");
}
if (cta.includes("-bottom-0.5")) {
  fail("Message gold hairline must sit inside the CTA, not clipped below it");
}
if (look.includes("<MaMark")) {
  fail("PDP breadcrumb must not repeat the mã already in the title");
}
if (cta.includes("feDisplacementMap") || header.includes("backdrop-filter: url")) {
  fail("CTA/header must not use displacement or backdrop-filter url()");
}
if (!header.includes("liquid-glass-bar") || !header.includes("ky-header-film")) {
  fail("Header must use Regular liquid glass with the static gold/ink metal hairline");
}
if (!header.includes("bottom-0 h-px") || header.includes("-bottom-0.5")) {
  fail("Category nav gold hairline must sit inside the tab row (not clipped by overflow)");
}
if (!css.includes(".ky-chrome-rim") || !css.includes("mask-composite: exclude")) {
  fail("CTA rim must be a masked Kelly Ying metal film");
}
if (css.includes("ky-rim-spin")) {
  fail("CTA rim must stay still — no compositor spin");
}
if (!css.includes(".ky-header-film") || !css.includes("color-mix(in srgb, var(--gold) 55%")) {
  fail("Header film must be a static gold color-mix hairline");
}
if (!css.includes(".ky-footer-film") || !read("components/footer.tsx").includes("ky-footer-film")) {
  fail("Footer must use the matching gold/ink hairline");
}
if (!css.includes(".ky-section-film") || !css.includes(".ky-split-hairline") || !css.includes(".ky-empty-rule")) {
  fail("Related, nav split, and empty wells must use gold hairlines");
}
if (!css.includes("overscroll-behavior-y: contain")) {
  fail("Page overscroll must not yank sticky chrome");
}
if (!css.includes("overflow-anchor: none")) {
  fail("Sticky chrome must not scroll-anchor the lookbook");
}
if (!css.includes("overflow-x: clip")) {
  fail("Page must clip sideways overscroll so peek rails do not yank the lookbook");
}
if (!css.includes("accent-color: var(--gold)") || !css.includes("caret-color: var(--gold)")) {
  fail("UA widgets and caret must stay gold with the lookbook");
}
if (!css.includes("@media (hover: none) and (pointer: coarse)") || !css.includes("font-size: 16px")) {
  fail("Touch fields must stay 16px so iOS does not zoom the lookbook");
}
if (!css.includes("@page")) {
  fail("Print must keep a paper margin around the look");
}
const shopLayout = read("app/(shop)/layout.tsx");
if (!shopLayout.includes('data-testid="shop-chrome"') || !shopLayout.includes("sticky top-0")) {
  fail("Announcement + header must stick as one notch-safe chrome stack");
}
if (shopLayout.includes("sticky top-0 z-50 bg-paper")) {
  fail("Sticky shop chrome must frost scrolling photos, not sit on opaque paper");
}
if (!shopLayout.includes("<SkipToLooks")) {
  fail("Skip to looks must stay in shop chrome");
}
const skip = read("components/skip-to-looks.tsx");
if (!skip.includes("focus:min-h-11")) {
  fail("Skip to looks must stay 44px when focused");
}
if (!skip.includes("focus:border-gold/45")) {
  fail("Skip to looks must keep a gold hairline when focused");
}
if (!skip.includes("focus:liquid-glass-chip")) {
  fail("Skip to looks must sit on Regular glass when focused");
}
if (!skip.includes("touch-manipulation")) {
  fail("Skip to looks must stay a tap target");
}
if (!skip.includes("select-none")) {
  fail("Skip to looks must not select on tap");
}
if (!skip.includes("whitespace-nowrap")) {
  fail("Skip to looks must stay one KY line when focused");
}
if (!skip.includes('translate="no"')) {
  fail("Skip to looks must not be auto-translated");
}
if (!skip.includes("SKIP_TO_LOOKS") || !skip.includes('pathname === "/" ? "#looks-heading" : "#main"')) {
  fail("Skip to looks must land on Looks at home, main on inner pages");
}
if (!shopLayout.includes("tabIndex={-1}") || !shopLayout.includes("outline-none")) {
  fail("Skip to looks must land in main without a page-sized gold ring");
}
if (!shopLayout.includes("scroll-mt-")) {
  fail("Skip to looks must clear sticky chrome");
}
if (!shopLayout.includes("<ShopPdpScroll") || !read("components/shop-pdp-scroll.tsx").includes('pathname.startsWith("/m/")')) {
  fail("Mã PDP must scroll to top so the title is not under sticky chrome");
}
if (!read("components/shop-pdp-scroll.tsx").includes("scrollTo(0, 0)")) {
  fail("Mã PDP scroll restore must jump to 0,0 without smooth interpolation");
}
if (!shopLayout.includes("<AnnouncementBar") || !shopLayout.includes("<Header")) {
  fail("Shop chrome must keep the announcement over the header");
}
if (header.includes("sticky top-0")) {
  fail("Header stickiness belongs on the chrome stack, not the header alone");
}
if (!header.includes("leading-[1.12]") || !header.includes("touch-manipulation") || !header.includes("min-h-11")) {
  fail("Header wordmark must not clip descenders; category tabs stay thumb-tall");
}
if (!header.includes("whitespace-nowrap")) {
  fail("Category tabs must stay one KY line in the rail");
}
if (!header.includes("min-w-0 max-w-full")) {
  fail("Header category rail must shrink instead of blowing the chrome");
}
if (!header.includes("select-none")) {
  fail("Header wordmark and category tabs must not select on tap");
}
if (!header.includes("text-balance")) {
  fail("Header wordmark must balance wrap");
}
if (!header.includes("truncate whitespace-nowrap")) {
  fail("Header wordmark must stay one KY line beside Message");
}
if (!header.includes('variant="header"') || !header.includes('className="shrink-0"')) {
  fail("Header Message must not shrink beside the wordmark");
}
if (!header.includes("<HeaderSearch") || !header.includes("<MessengerCta")) {
  fail("Header must keep compact search and Messenger on every shop page");
}
if (!header.includes("h-14") || !read("components/header-search.tsx").includes("min-h-11")) {
  fail("Header search must stay usable in the h-14 row");
}
if (!read("components/header-search.tsx").includes("safe-area-inset-right")) {
  fail("Header search hits must pad the landscape home indicator");
}
if (!read("components/header-search.tsx").includes("LOOK_SEARCH_ARIA") || !read("components/header-search.tsx").includes("shop-header-search-toggle")) {
  fail("Header search must stay bilingual and expand on the phone row");
}
if (featured.includes("shop-header-search") || featured.includes("Tìm mã hoặc tên")) {
  fail("Looks must not host a second search box; header is the source of truth");
}
if (!featured.includes("filterLooksByQuery") || !featured.includes("committedQuery")) {
  fail("Looks must honor header search via the shared look-search helper");
}
if (!shopLayout.includes("ShopSearchProvider") || !shopLayout.includes("<Header")) {
  fail("Shop layout must feed live looks to header search on every page including PDP");
}
if (!header.includes("hover-hover:hover:text-gold-deep")) {
  fail("Header wordmark must gold-up on hover pointers");
}
if (!header.includes("safe-area-inset-left") || !header.includes("safe-area-inset-right")) {
  fail("Header must pad landscape home indicators");
}
if (!header.includes("Danh mục · Categories")) {
  fail("Category nav aria must stay bilingual like gallery photo labels");
}
if (!header.includes("scroll-pl-[max(1.25rem,env(safe-area-inset-left,0px))]")) {
  fail("Category nav must keep scroll padding so the last tab is not flush");
}
if (!header.includes("ky-h-scroll-cue") || !featured.includes("ky-h-scroll-cue") || !css.includes(".ky-h-scroll-cue")) {
  fail("Category and Looks tabs must cue horizontal scroll on the phone");
}
if (header.includes("sm:justify-center")) {
  fail("Category rail must start-align so Tops is not clipped when 12 Boss tabs overflow");
}
if (featured.includes("sm:justify-center")) {
  fail("Looks filter rail must start-align so 12 category tabs are not clipped");
}
if (!header.includes("justify-start")) {
  fail("Category rail must start-align");
}
if (!header.includes("categoryAriaLabel")) {
  fail("Category tabs must keep recorded VN · EN aria");
}
if (!header.includes("ky-split-hairline")) {
  fail("Category row must split from the wordmark with a gold hairline");
}
if (!header.includes('pathname === "/" ? "page"')) {
  fail("Header wordmark must mark the home page current");
}
if (!header.includes("scrollChromeChildIntoView") || !header.includes('[aria-current="page"]')) {
  fail("Category nav must keep the current tab in the rail via scrollLeft");
}
if (header.includes("scrollIntoView")) {
  fail("Category nav must not use page scrollIntoView");
}
if (!header.includes("holdTimer") || !header.includes("clearTimeout")) {
  fail("Header long-press admin must clear its timer on unmount");
}
if (!header.includes('translate="no"')) {
  fail("Header wordmark and category names must not be auto-translated");
}
const footer = read("components/footer.tsx");
if (!footer.includes("safe-area-inset-bottom") || footer.includes("tracking-[0.04em]")) {
  fail("Footer must pad the home indicator and match Looks tracking");
}
if (!footer.includes("text-balance")) {
  fail("Footer wordmark must balance wrap");
}
if (!footer.includes('startsWith("/m/")') || !footer.includes("shop-buy-bar-spacer") || !footer.includes("--shop-buy-bar-space")) {
  fail("PDP footer must clear the phone buy bar");
}
if (!footer.includes('href="/"') || !footer.includes("aria-current") || !footer.includes("min-h-11")) {
  fail("Footer wordmark must go home and stay thumb-tall");
}
if (!footer.includes('translate="no"')) {
  fail("Footer wordmark must not be auto-translated");
}
if (!footer.includes("select-none")) {
  fail("Footer wordmark must not select on tap");
}
if (!footer.includes("whitespace-nowrap") || !footer.includes("truncate")) {
  fail("Footer wordmark must stay one KY line");
}
if (!footer.includes("hover-hover:hover:text-gold-deep")) {
  fail("Footer wordmark must gold-up on hover pointers");
}
if (!footer.includes("pt-10 sm:pt-12")) {
  fail("Footer must keep editorial paper padding");
}
if (!roll.includes("photoIndexLabel") || !roll.includes("Xem ảnh lớn · View larger") || !roll.includes("touch-manipulation")) {
  fail("Neighbor gallery taps must stay bilingual like View larger");
}
if (!roll.includes("h-11 min-w-11")) {
  fail("Gallery dots must stay a 44px hit target around the gold pill");
}
if (!roll.includes("touch-manipulation select-none items-center justify-center")) {
  fail("Gallery arrows and dots must not select glyphs on tap");
}
if (!roll.includes("scrollCurrentChromeIntoView") || !roll.includes("dotsRailRef")) {
  fail("Gallery dots must keep the current pill in the capsule via scrollLeft");
}
if (!roll.includes("scrollRailToChild") || roll.includes("scrollIntoView")) {
  fail("Gallery photo rail must snap with rail scrollLeft, not page scrollIntoView");
}
if (!roll.includes("aria-posinset") || !roll.includes("aria-setsize")) {
  fail("Gallery dots must keep APG posinset");
}
if (!roll.includes("aria-hidden")) {
  fail("Gallery gold pills must stay decorative inside the labeled dots");
}
if (!gallery.includes("PlaceholderTile") || !gallery.includes("morePhotosLabel")) {
  fail("Empty gallery must use the look placeholder; overflow stays bilingual");
}
if (!gallery.includes("galleryReelLabel") || !gallery.includes('role="img"')) {
  fail("Empty gallery well must name this mã’s photos for assistive tech");
}
if (!gallery.includes("border-gold/45")) {
  fail("Empty gallery well must keep a quiet gold rim");
}
if (!gallery.includes("photoPositionLabel") || !gallery.includes("overflow-x-auto tab-scroll")) {
  fail("Gallery live region must name position; thumbs must be a tab-scroll rail");
}
if (!gallery.includes("{safeIndex + 1} / {slides.length}")) {
  fail("Gallery must print a quiet photo index under the thumbs");
}
if (!gallery.includes("mt-2 max-w-full truncate whitespace-nowrap")) {
  fail("Gallery photo index must stay one KY line");
}
if (!gallery.includes("scrollCurrentChromeIntoView") || !gallery.includes("thumbRailRef")) {
  fail("Gallery thumbs must keep the current shot in the rail via scrollLeft");
}
if (!gallery.includes("aria-current={safeIndex >= THUMB_CAP}")) {
  fail("Overflow +N must mark current when the shot is past the thumb cap");
}
if (!gallery.includes("ky-thumb-rail") || !gallery.includes("border-gold/35")) {
  fail("Gallery thumbs must keep a quiet gold rim and kill the iOS callout");
}
if (!gallery.includes("ky-thumb-rail mt-3 flex min-w-0 max-w-full flex-nowrap")) {
  fail("Gallery thumb rail must shrink instead of blowing the PDP column");
}
if (!gallery.includes("border-gold/35 hover-hover:hover:border-gold") || !gallery.includes("draggable={false}")) {
  fail("Idle gallery thumbs must gold-up on hover pointers; thumbs must not drag");
}
if (!gallery.includes("photoIndexLabel") || !gallery.includes("touch-manipulation")) {
  fail("Gallery thumbs must share the rail photo labels");
}
if (!gallery.includes('aria-haspopup="dialog"')) {
  fail("More-photos control must mark the lightbox as a dialog popup");
}
if (!gallery.includes("liquid-glass-chip") || gallery.includes("bg-blush text-[11px]")) {
  fail("Overflow +N must be a glass chip, not a blush tile");
}
if (!gallery.includes("<span aria-hidden>+{overflowCount}</span>") || !gallery.includes("select-none")) {
  fail("Overflow +N must stay decorative; empty-well Message must not select");
}
if (!gallery.includes("ky-thumb-shot relative min-h-11 min-w-11 shrink-0 touch-manipulation select-none")) {
  fail("Gallery thumbs must not select on tap");
}
if (!gallery.includes("shrink-0 touch-manipulation select-none items-center justify-center")) {
  fail("Overflow +N must not select on tap");
}
if (!gallery.includes("items-center justify-center whitespace-nowrap border border-gold/35")) {
  fail("Overflow +N must stay one KY line");
}
if (!gallery.includes("pointer-events-none absolute inset-x-0 bottom-5")) {
  fail("Empty-well Message overlay must not steal taps");
}
if (!gallery.includes("select-none\" aria-hidden")) {
  fail("Empty-well Message overlay must stay decorative over the placeholder");
}
if (!gallery.includes("width={64}")) {
  fail("Gallery thumbs must declare intrinsic size so the rail does not jump");
}
if (!gallery.includes("aria-posinset")) {
  fail("Gallery thumbs must keep APG posinset");
}
if (!gallery.includes('sizes="(min-width: 640px) 72px, 64px"')) {
  fail("Gallery thumbs must declare a thumb-sized sizes hint");
}
if (!gallery.includes("object-top")) {
  fail("Gallery thumbs must match cover crop");
}
if (!lightbox.includes("touch-manipulation") || !lightbox.includes("leading-[1.08]")) {
  fail("Lightbox close/nav/thumbs must stay thumb-tall; serif title must not clip");
}
if (!lightbox.includes("h-11 w-11 touch-manipulation select-none")) {
  fail("Lightbox close must not select on tap");
}
if (!lightbox.includes("mb-3 flex min-w-0 items-start justify-between gap-3")) {
  fail("Lightbox title must shrink so the close hit stays 44px");
}
if (!lightbox.includes("mt-1 max-w-full truncate whitespace-nowrap")) {
  fail("Lightbox color index must stay one KY line");
}
if (!lightbox.includes("h-11 min-w-11 touch-manipulation select-none")) {
  fail("Lightbox dots must not select on tap");
}
if (!lightbox.includes("ky-thumb-shot min-h-11 min-w-11 shrink-0 touch-manipulation select-none")) {
  fail("Lightbox thumbs must not select on tap");
}
if (!lightbox.includes("inert = true")) {
  fail("Lightbox must inert the shop behind the dialog");
}
if (!lightbox.includes("document.documentElement.style.overflow") || !lightbox.includes("tabIndex={-1}")) {
  fail("Lightbox must lock html scroll and keep the veil out of the tab cycle");
}
if (!lightbox.includes("node.tabIndex >= 0")) {
  fail("Lightbox Tab trap must skip the veil");
}
if (!lightbox.includes("<span aria-hidden>")) {
  fail("Lightbox close and arrows must stay decorative inside labeled buttons");
}
if (!lightbox.includes('translate="no"')) {
  fail("Lightbox look names must not be auto-translated");
}
if (!lightbox.includes("width={56}")) {
  fail("Lightbox thumbs must declare intrinsic size so the rail does not jump");
}
if (!lightbox.includes("aria-posinset") || !lightbox.includes("aria-setsize")) {
  fail("Lightbox thumbs must keep APG posinset");
}
if (!lightbox.includes('sizes="56px"')) {
  fail("Lightbox thumbs must declare a thumb-sized sizes hint");
}
if (!lightbox.includes("object-top")) {
  fail("Lightbox thumbs must match cover crop");
}
if (!lightbox.includes("photoIndexLabel")) {
  fail("Lightbox alts and thumbs must share the rail photo labels");
}
if (!lightbox.includes('case "Home"') || !lightbox.includes('case "End"')) {
  fail("Lightbox must keep Home / End with the arrow keys");
}
if (!lightbox.includes("aria-controls={controlsId}") || !lightbox.includes("id={railId}")) {
  fail("Lightbox arrows and thumbs must control the snap rail");
}
if (!lightbox.includes('sizes="(min-width: 768px) 48rem, 100vw"')) {
  fail("Lightbox photos must declare a sizes hint");
}
if (!lightbox.includes("photoPositionLabel") || !lightbox.includes("border-gold/45")) {
  fail("Lightbox counter aria must stay bilingual; close rim stays gold on touch");
}
if (!lightbox.includes("tabular-nums") || !lightbox.includes("hover-hover:hover:border-gold")) {
  fail("Lightbox photo index must stay tabular; close/thumbs gold-up on hover pointers");
}
if (!lightbox.includes("flex-nowrap") || !lightbox.includes("overflow-x-auto")) {
  fail("Lightbox thumbs must be a one-row tab-scroll rail");
}
if (!lightbox.includes("w-max max-w-full") || !lightbox.includes("overflow-x-auto tab-scroll")) {
  fail("Lightbox dots must scroll inside the glass capsule");
}
if (!lightbox.includes("scrollCurrentChromeIntoView") || !lightbox.includes("dotsRailRef") || !lightbox.includes("thumbRailRef")) {
  fail("Lightbox dots and thumbs must keep the current chrome in view via scrollLeft");
}
if (!lightbox.includes("scrollRailToChild") || lightbox.includes("scrollIntoView")) {
  fail("Lightbox photo rail must snap with rail scrollLeft, not page scrollIntoView");
}
if (!lightbox.includes("ky-thumb-rail") || !lightbox.includes("overscroll-contain")) {
  fail("Lightbox thumbs must kill the iOS callout; veil must contain overscroll");
}
if (!lightbox.includes("ky-thumb-rail mt-3 flex min-w-0 max-w-full flex-nowrap")) {
  fail("Lightbox thumb rail must shrink instead of blowing the veil");
}
const collections = read("components/collection-list.tsx");
if (
  !collections.includes("aria-label=\"Bộ sưu tập · Collections\"") ||
  !collections.includes("snap-x") ||
  !collections.includes("snap-center") ||
  !collections.includes("snap-always") ||
  !collections.includes("w-[42%]") ||
  !collections.includes("tab-scroll") ||
  !collections.includes("whitespace-nowrap") ||
  !collections.includes("ky-collection-rail")
) {
  fail("Phone collection must be a one-row snap peek so Looks can clear sticky chrome");
}
if (!collections.includes("min-w-0 max-w-full")) {
  fail("Collection peek rail must shrink instead of blowing the home grid");
}
if (!collections.includes("categoryAriaLabel")) {
  fail("Collection tile alts must stay bilingual from recorded category names");
}
if (!collections.includes('alt=""') || !collections.includes("aria-posinset")) {
  fail("Collection photos must stay decorative inside bilingual tile links; tiles keep APG posinset");
}
if (!collections.includes("translate=\"no\" aria-hidden")) {
  fail("Collection labels must stay visual-only inside bilingual tile links");
}
if (!collections.includes("scale-x-100") || !collections.includes("bg-gold/45")) {
  fail("Collection tiles must keep a quiet gold hairline on touch (not hover-only)");
}
if (!collections.includes('bg-gold/45" aria-hidden') || !collections.includes("sizes=")) {
  fail("Collection gold hairline must stay decorative; tiles must declare sizes");
}
if (!collections.includes("bg-gradient-to-t") || !collections.includes("to-transparent\" aria-hidden")) {
  fail("Collection photo film must stay decorative");
}
if (!collections.includes("from-ink/20")) {
  fail("Collection film must stay a quiet ink veil");
}
if (collections.includes("from-ink/28")) {
  fail("Collection film must not dump a 28% wash on the tile");
}
if (!collections.includes("tracking-[0.16em]")) {
  fail("Collection tile labels must match Looks tab tracking");
}
if (!collections.includes("motion-safe:hover-hover:group-hover:scale-[1.04]")) {
  fail("Collection zoom must be motion-safe and hover-only (no iPhone sticky hover)");
}
if (collections.includes("scale-105") || collections.includes("scale-[1.08]") || collections.includes("duration-700")) {
  fail("Collection zoom must stay quiet (1.04 / 500ms), not a punchy Ken Burns");
}
if (!collections.includes("motion-safe:duration-500")) {
  fail("Collection zoom duration must match look-card lift");
}
if (!collections.includes("object-top")) {
  fail("Collection tiles must pin object-top so garments are not cropped at the neck");
}
if (!collections.includes("draggable={false}")) {
  fail("Collection tiles must not drag off the rail on iOS");
}
if (!collections.includes('fetchPriority={index < 2 ? "high" : "auto"}')) {
  fail("First collection tiles must load eager so Looks is not waiting on lazy covers");
}
if (!collections.includes("liquid-glass-caption")) {
  fail("Collection labels must be glass captions over the photo");
}
if (!collections.includes("pointer-events-none absolute inset-x-0 bottom-4")) {
  fail("Collection labels must not steal taps from the tile");
}
if (!collections.includes("touch-manipulation select-none")) {
  fail("Collection tiles must not select on tap");
}
if (!collections.includes("max-w-[calc(100%-1rem)]") || !collections.includes("truncate")) {
  fail("Collection labels must clip inside the 42% peek tile, not a dead overflow rail");
}
if (!collections.includes("text-[10px]") || !collections.includes("md:text-[11px]") || !collections.includes("md:tracking-[0.16em]")) {
  fail("Collection peek labels must tighten so ACCESSORIES fits the 42% tile");
}
if (!collections.includes("tracking-[0.08em]") || !collections.includes("px-1 py-1.5")) {
  fail("Collection peek labels must tighten tracking/padding so ACCESSORIES fits without invented copy");
}
if (collections.includes("px-1.5") || collections.includes("tracking-[0.12em]")) {
  fail("Collection peek labels must not keep the wide 0.12em / px-1.5 chip on 42% tiles");
}
const categoryPage = read("app/(shop)/c/[slug]/page.tsx");
if (!categoryPage.includes("scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)]")) {
  fail("Category heading must clear sticky chrome");
}
if (!categoryPage.includes("outline-none")) {
  fail("Category heading must not show a page-sized gold ring");
}
if (!categoryPage.includes("truncate whitespace-nowrap")) {
  fail("Category look count must stay one KY line");
}
const notFound = read("app/not-found.tsx");
if (!notFound.includes("border-gold/45") || !notFound.includes("select-none")) {
  fail("Not found Back to shop must keep a gold rim and not select on tap");
}
if (!notFound.includes("whitespace-nowrap")) {
  fail("Not found Back to shop must stay one KY line");
}
if (collections.includes("group-hover:scale-x-100")) {
  fail("Collection gold hairline must not be hover-only");
}
if (!featured.includes("pb-1") || !featured.includes("min-h-11")) {
  fail("Featured tab gold must sit inside the scroller; tabs stay 44px");
}
if (!featured.includes("min-w-0 max-w-full overflow-x-auto pb-1 tab-scroll")) {
  fail("Featured tab rail must shrink instead of blowing Looks");
}
if (!featured.includes("leading-[1.08]")) {
  fail("Looks heading must not clip serif descenders");
}
if (!featured.includes("py-10")) {
  fail("Phone Looks section must stay compact after the collection peek");
}
if (!featured.includes("uppercase tracking-[0.16em]")) {
  fail("Featured tabs stay quieter 0.16em vs header 0.18em");
}
if (!featured.includes("select-none")) {
  fail("Featured tabs must not select on tap");
}
if (!featured.includes("mx-auto mt-3 max-w-full truncate whitespace-nowrap")) {
  fail("Looks count must stay one KY line");
}
if (!featured.includes("text-muted tabular-nums")) {
  fail("Look counts must stay tabular");
}
if (!featured.includes("ky-gutter") || !featured.includes("ky-gutter-bleed")) {
  fail("Featured Looks and tab rail must use KY landscape gutters");
}
if (!featured.includes('aria-label="Lọc looks · Filter looks"')) {
  fail("Featured tablist must stay bilingual like gallery photo labels");
}
if (!css.includes(".ky-gutter") || !css.includes(".ky-gutter-bleed")) {
  fail("Shop gutters must pad landscape safe-area");
}
if (!css.includes("--shop-buy-bar-space") || !css.includes("5.5rem + env(safe-area-inset-bottom, 0px)")) {
  fail("Phone buy-bar clearance must use a shared space token that still clears 5.5rem + home indicator");
}
if (!css.includes("@custom-variant hover-hover") || !css.includes("@media (hover: hover)")) {
  fail("Hover lift/scale must live under hover-hover so touch stays tap-only");
}
if (!css.includes("text-rendering: optimizeLegibility") || !css.includes("hyphens: none")) {
  fail("Look names must not hyphenate; display serif must stay legible");
}
if (!css.includes("font-kerning: normal")) {
  fail("Display serif must keep kerning on look names");
}
if (!css.includes("font-variant-ligatures: common-ligatures")) {
  fail("Display serif must keep common ligatures on look names");
}
if (!css.includes("font-synthesis: none")) {
  fail("Look names and mãs must not faux-bold");
}
if (!css.includes("overscroll-behavior-x: contain")) {
  fail("Tab rails must contain horizontal overscroll");
}
const pdpTitle = read("components/product-page-title.tsx");
if (!pdpTitle.includes('text-[11px] tracking-[0.16em] text-muted') || pdpTitle.includes("text-[1.35rem]")) {
  fail("PDP mã must stay a quiet kicker beside the serif name");
}
if (!pdpTitle.includes("leading-[1.08]") || pdpTitle.includes("leading-[0.95]")) {
  fail("PDP serif name must not clip descenders");
}
if (!pdpTitle.includes("select-all")) {
  fail("PDP mã must be select-all so Copy mã is not the only way to grab it");
}
if (!pdpTitle.includes("min-w-0") || !pdpTitle.includes("scroll-mt-")) {
  fail("PDP title must shrink in the grid and clear sticky chrome");
}
if (!pdpTitle.includes("outline-none")) {
  fail("PDP title must not show a page-sized gold ring");
}
if (!pdpTitle.includes('id="look-title"') || !look.includes('aria-labelledby="look-title"')) {
  fail("PDP article must be labelled by the look title");
}
if (!read("components/ma-mark.tsx").includes('translate="no"')) {
  fail("Mã marks must not be auto-translated");
}
if (!read("components/ma-mark.tsx").includes("shrink-0")) {
  fail("Mã marks must not crush in a wrapping title row");
}
const price = read("components/product-price.tsx");
if (!price.includes("tabular-nums") || price.includes("InboxPriceLabel") === false) {
  fail("Printed USD must be tabular; Inbox for price stays a phrase");
}
if (!price.includes("select-all")) {
  fail("Printed USD must be select-all so Copy mã is not the only way to grab a price");
}
if (!price.includes("whitespace-nowrap")) {
  fail("Printed USD must stay on one line");
}
const inboxFn = price.split("function InboxPriceLabel")[1]?.split("export function ProductPrice")[0] ?? "";
if (!inboxFn.includes("whitespace-nowrap")) {
  fail("Inbox for price must stay one KY line like printed USD");
}
if (!price.includes('translate="no"')) {
  fail("Printed USD and Inbox for price must not be auto-translated");
}
if (!pdpTitle.includes("text-balance") || !card.includes("text-balance")) {
  fail("Look names must balance wrap on phone");
}
if (!card.includes("min-w-0 font-display")) {
  fail("Look card serif names must shrink in the two-column grid");
}
if (!card.includes("reduced ? { duration: 0 }")) {
  fail("Look cards must not spring when Reduce Motion is on");
}
if (!card.includes("tracking-[0.02em]")) {
  fail("Look card serif name must match PDP tracking");
}
if (/backdrop-filter:\s*url\(|backdrop-filter: url\(/.test(css)) {
  fail("Never use backdrop-filter: url() (iPhone header hole)");
}
if (css.includes("feDisplacementMap") || css.includes("feTurbulence") || css.includes("LiquidMetal")) {
  fail("Liquid chrome must stay shader-light — no displacement / Paper metal");
}
if (image.includes("filter: url") || roll.includes("filter: url") || image.includes("ky-chrome-rim")) {
  fail("Chrome rim/goo must never wrap cover photos");
}
if (featured.includes("ArrowUp") || featured.includes("ArrowDown")) {
  fail("Featured tabs must not steal Up/Down from page scroll");
}
if (grid.includes("tile-${") || featured.includes("layoutId={`tile-")) {
  fail("Recipe A pour must not also FLIP tile-${ma}");
}
if (!featured.includes("layoutScroll")) {
  fail("Featured tab scroller must layoutScroll");
}
if (!featured.includes('id="featured-tabs"')) {
  fail("Tab meniscus must be namespaced in LayoutGroup featured-tabs");
}
if (!featured.includes("lookCountLabel(count)")) {
  fail("Featured tabs must name looks in the accessible label (not pieces)");
}
if (!featured.includes('text-muted/80"}`} aria-hidden')) {
  fail("Featured tab counts must stay visual-only inside the bilingual aria-label");
}
if (!featured.includes("FEATURED_ALL_ARIA") || !featured.includes("categoryAriaLabel")) {
  fail("Featured tab aria must stay bilingual from recorded category names");
}
if (!featured.includes("text-balance") || !featured.includes("scroll-mt-")) {
  fail("Looks heading must balance wrap and clear sticky chrome");
}
if (!grid.includes("replay={false}")) {
  fail("Featured pour must not restagger the whole grid");
}
if (!header.includes('layoutId={reduced ? undefined : "nav-tab"}')) {
  fail("Category nav must keep a gold hairline layoutId");
}
if (header.includes("FILTER_POUR_SECONDS") || header.includes("times: [0, 0.42, 1]") || header.includes("scaleX: [1, 1.12, 1]")) {
  fail("Nav hairline must not overshoot");
}

if (FILTER_FADE_SECONDS > 0.2 || COLOR_FADE_SECONDS > 0.25) {
  fail("Filter / color fade budgets drifted past Official #31");
}
if (FILTER_SLIDE_SECONDS < 0.24 || FILTER_SLIDE_SECONDS > 0.32) {
  fail("Looks slide must stay ~280ms (quiet ease, not a watery pour)");
}
if (GALLERY_ROLL_MS < 380 || GALLERY_ROLL_MS > 480) {
  fail("Color/peek roll must stay viscous ~380–480ms (Fast off)");
}
if (!read("lib/gallery-snap.ts").includes("export function animateGalleryScrollTo")) {
  fail("Gallery roll must be RAF viscosity, not Motion-drag");
}
if (!read("lib/gallery-snap.ts").includes("export function scrollChromeChildIntoView")) {
  fail("Chrome rails must scroll via scrollLeft, not page scrollIntoView");
}
if (!read("lib/gallery-snap.ts").includes("export function scrollRailToChild")) {
  fail("Photo rails must snap with scrollRailToChild");
}
if (!read("lib/gallery-snap.ts").includes("rail.scrollLeft +=")) {
  fail("Chrome into-view must use rail scrollLeft delta");
}
if (read("lib/gallery-snap.ts").includes(".scrollIntoView")) {
  fail("Gallery snap helpers must never call scrollIntoView");
}
if (read("lib/gallery-snap.ts").includes("scrollChromeChildIntoView") && read("lib/gallery-snap.ts").includes("current.scrollIntoView")) {
  fail("Chrome helper must never call scrollIntoView on the child");
}

const hidden = fadeUp(false).hidden as { opacity: number };
if (hidden.opacity !== 1) {
  fail("fadeUp hidden must paint at opacity 1 (no blank covers)");
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(process.cwd(), "data/products.json"), "utf8")) as unknown,
);
const shop = shopVisibleProducts(seed.products);
const accessories = shop.filter((product) => product.type === "P");
if (!accessories.some((product) => product.ma === "P02") || !accessories.some((product) => product.ma === "P05")) {
  fail("Accessories filter must keep Hold P02 and P05");
}
if (shop.some((product) => product.ma === "Q01")) {
  fail("Do not invent Q01 for empty Bottoms");
}
const pdpPage = read("app/(shop)/m/[ma]/page.tsx");
if (!pdpPage.includes("ProductLook") || pdpPage.includes("namedCovers={false}")) {
  fail("Related tiles keep product-{their mã}; the hero 3/4 frame is product-THIS");
}
if (!pdpPage.includes("--shop-buy-bar-space") || !pdpPage.includes("md:pb-0")) {
  fail("PDP page must clear the phone buy bar the same way the footer does");
}
if (!pdpPage.includes("ky-section-film") || !pdpPage.includes("related-heading")) {
  fail("Related looks must sit under a gold section hairline");
}
if (!pdpPage.includes("tracking-[0.03em]")) {
  fail("Related heading must match Looks tracking, not footer 0.04em");
}
if (!pdpPage.includes("scroll-mt-[calc(env(safe-area-inset-top,0px)+8.25rem)]")) {
  fail("Related heading must clear sticky chrome");
}
if (!pdpPage.includes("outline-none")) {
  fail("Related heading must not show a page-sized gold ring");
}
if (!pdpPage.includes("truncate whitespace-nowrap")) {
  fail("Related look count must stay one KY line");
}
if (galleryPeekEdge(0, 1) !== "none") {
  fail("n=1 must not grow a paper-edge mask");
}
if (galleryPeekEdge(0, 3) !== "start" || galleryPeekEdge(2, 3) !== "end" || galleryPeekEdge(1, 3) !== "both") {
  fail("Peek mask must fade only the neighbor edge");
}
if (clampGalleryIndex(-1, 4) !== 0 || clampGalleryIndex(9, 4) !== 3) {
  fail("Gallery index must clamp, never wrap");
}
const shopGalleryFiles = [
  "components/product-gallery.tsx",
  "components/gallery-peek-roll.tsx",
  "components/photo-lightbox.tsx",
  "lib/product-media.ts",
];
for (const rel of shopGalleryFiles) {
  const text = read(rel);
  if (text.includes("001.jpg") || text.includes("002.jpg")) {
    fail(`${rel} must not invent 001/002 files`);
  }
}
const emptyCopy = read("lib/look-count.ts");
if (!emptyCopy.includes("No ${label.toLowerCase()} listed.") || !emptyCopy.includes("Chưa có ${vn} trên lookbook")) {
  fail("Empty /c/quan must stay copy-only");
}
if (!emptyCopy.includes("TYPE_LABELS") || !emptyCopy.includes("categoryFromSlug")) {
  fail("Empty collections must use recorded category names, never invented copy");
}
if (!read("components/shop-empty.tsx").includes("ky-empty-rule")) {
  fail("Empty collection well must use a gold rule, not a gray box");
}
if (!read("components/shop-empty.tsx").includes("liquid-glass-sheet")) {
  fail("Empty wells must sit in Regular glass, not a paper void");
}
if (!read("components/shop-empty.tsx").includes("text-pretty")) {
  fail("Empty collection copy must wrap pretty");
}
if (!read("components/shop-empty.tsx").includes('translate="no"')) {
  fail("Empty collection copy must not be auto-translated");
}
if (!read("components/shop-empty.tsx").includes("outline-none")) {
  fail("Empty collection title must not show a page-sized gold ring");
}
if (!read("app/(shop)/error.tsx").includes("hover-hover:hover:border-gold")) {
  fail("Shop error Try again must gold-up on hover pointers");
}
if (!read("app/(shop)/error.tsx").includes("border-gold/45")) {
  fail("Shop error Try again must keep a quiet gold rim so hover gold is visible");
}
if (!read("app/(shop)/error.tsx").includes("liquid-glass-chip") || !read("app/(shop)/error.tsx").includes("liquid-glass-sheet")) {
  fail("Shop error must use a glass sheet and Try again chip");
}
const adminSaveBar = read("app/admin/item-form.tsx");
if (adminSaveBar.includes("bg-paper/95")) {
  fail("Admin save bar must not use milky paper/95");
}
if (!adminSaveBar.includes("liquid-glass-bar") || !adminSaveBar.includes("ky-chrome-blur")) {
  fail("Admin save bar must share Regular liquid glass");
}
if (!adminSaveBar.includes("safe-area-inset-left") || !adminSaveBar.includes("safe-area-inset-right")) {
  fail("Admin save bar must pad landscape home indicators");
}
if (!adminSaveBar.includes("safe-area-inset-bottom, 0px")) {
  fail("Admin save bar must pad the home indicator");
}
if (!adminSaveBar.includes("saveBarLabel") || !adminSaveBar.includes('const _exhaustive: never = mode')) {
  fail("Admin save label must be an exhaustive add/edit switch");
}
const settingsPanel = read("app/admin/settings-panel.tsx");
if (!settingsPanel.includes("Remove") || !settingsPanel.includes("min-h-11 shrink-0")) {
  fail("Settings Remove must stay thumb-tall");
}
if (!settingsPanel.includes("Add line") || !settingsPanel.includes("inline-flex min-h-11 touch-manipulation")) {
  fail("Settings Add line must stay thumb-tall");
}
if (!settingsPanel.includes("leading-[1.08]")) {
  fail("Site settings headings must not clip serif descenders");
}
if (
  !settingsPanel.includes('name="import-mode"') ||
  !settingsPanel.includes("inline-flex min-h-11 items-center gap-2 touch-manipulation select-none")
) {
  fail("Catalog import mode radios must stay thumb-tall");
}
if (!gallery.includes("liquid-glass-caption") || !gallery.includes('data-testid="gallery-empty"')) {
  fail("Empty gallery caption must be glass over the placeholder");
}
if (!read("app/(shop)/error.tsx").includes('role="alert"')) {
  fail("Shop error must be an alert");
}
if (!read("app/(shop)/error.tsx").includes("select-none")) {
  fail("Shop error Try again must not select on tap");
}
if (!read("app/(shop)/error.tsx").includes("whitespace-nowrap")) {
  fail("Shop error Try again must stay one KY line");
}
if (!read("app/(shop)/error.tsx").includes("outline-none")) {
  fail("Shop error title must not show a page-sized gold ring");
}
if (!read("app/admin/error.tsx").includes("hover-hover:hover:border-gold")) {
  fail("Admin error Try again must gold-up on hover pointers");
}
if (!read("app/admin/error.tsx").includes("border-gold/45")) {
  fail("Admin error Try again must keep a quiet gold rim so hover gold is visible");
}
if (!read("app/admin/error.tsx").includes("select-none")) {
  fail("Admin error actions must not select on tap");
}
if (!read("app/admin/error.tsx").includes("hover-hover:hover:opacity-90")) {
  fail("Admin error Open catalog must dim on hover pointers");
}
if (!read("app/admin/error.tsx").includes("leading-[1.08]")) {
  fail("Admin error heading must not clip serif descenders");
}
if (!read("app/admin/error.tsx").includes("touch-manipulation")) {
  fail("Admin error actions must stay tap targets");
}
if (!read("app/admin/error.tsx").includes("whitespace-nowrap")) {
  fail("Admin error Sell ops kicker must stay one KY line");
}
if (!read("app/admin/error.tsx").includes("safe-area-inset-left") || !read("app/admin/error.tsx").includes("safe-area-inset-right")) {
  fail("Admin error must pad landscape home indicators");
}
if (!read("app/admin/frame.tsx").includes("safe-area-inset-left") || !read("app/admin/frame.tsx").includes("safe-area-inset-right")) {
  fail("Admin frame must pad landscape home indicators");
}
if (!read("app/admin/error.tsx").includes("items-center whitespace-nowrap rounded-full bg-ink")) {
  fail("Admin error Open catalog must stay one KY line");
}
if (!read("app/admin/error.tsx").includes("items-center whitespace-nowrap rounded-full border border-gold/45")) {
  fail("Admin error Try again must stay one KY line");
}
if (!read("components/asia-fit.tsx").includes("liquid-glass-sheet") || !read("components/asia-fit.tsx").includes("pdp-lightbox-veil")) {
  fail("Fit cm sheet must use Regular glass over a veil, not opaque paper");
}
if (!read("components/asia-fit.tsx").includes("safe-area-inset-bottom") || !read("components/asia-fit.tsx").includes("safe-area-inset-left") || !read("components/asia-fit.tsx").includes("safe-area-inset-right")) {
  fail("Fit cm sheet must pad landscape home indicators");
}
if (read("components/asia-fit.tsx").includes("rgba(17,17,17,0.45)")) {
  fail("Fit cm sheet must not drop a 45% ink shadow");
}
if (!read("components/asia-fit.tsx").includes("rgba(17,17,17,0.28)")) {
  fail("Fit cm sheet must stay a quiet ink veil");
}
if (!read("components/asia-fit.tsx").includes("min-h-11")) {
  fail("Fit cm open/close must stay thumb-tall");
}
if (!read("components/asia-fit.tsx").includes("leading-[1.08]")) {
  fail("Fit cm heading must not clip serif descenders");
}
if (!read("app/admin/console.tsx").includes("items-center whitespace-nowrap rounded-md")) {
  fail("Admin nav Catalog / Add mã must stay one KY line");
}
if (!read("app/admin/toasts.tsx").includes("min-h-11")) {
  fail("Admin toast Close must stay thumb-tall");
}
if (!read("app/admin/toasts.tsx").includes("select-none") || !read("app/admin/toasts.tsx").includes("hover-hover:hover:opacity-80")) {
  fail("Admin toast Close must not select on tap; dim on hover pointers");
}
if (!read("app/admin/toasts.tsx").includes("whitespace-nowrap")) {
  fail("Admin toast Close must stay one KY line");
}
if (read("app/admin/toasts.tsx").includes("shadow-lg") || read("app/admin/toasts.tsx").includes("right-4")) {
  fail("Admin toast must not use a cheap drop or sit flush in landscape");
}
if (!read("app/admin/toasts.tsx").includes("rgba(17,17,17,0.28)")) {
  fail("Admin toast must stay a quiet ink veil");
}
if (!read("app/admin/toasts.tsx").includes("safe-area-inset-right")) {
  fail("Admin toast must pad the landscape home indicator");
}
if (!read("app/admin/fields.tsx").includes("whitespace-nowrap")) {
  fail("Admin field labels must stay one KY line");
}
if (read("app/admin/fields.tsx").includes("block max-w-full truncate whitespace-nowrap text-xs uppercase tracking-[0.14em] text-muted")) {
  fail("Admin Field/Area must not truncate the wrapping control");
}
if (
  !read("app/admin/fields.tsx").includes("AdminKickerLabel") ||
  !read("app/admin/fields.tsx").includes('span className="block max-w-full truncate whitespace-nowrap"')
) {
  fail("Admin field kickers must clip on an inner span");
}
if (!read("app/admin/catalog-list.tsx").includes("inline-flex min-h-11 items-center touch-manipulation select-none whitespace-nowrap text-xs uppercase tracking-[0.12em] text-ink")) {
  fail("Catalog Edit must stay thumb-tall");
}
if (!read("app/admin/catalog-list.tsx").includes("leading-[1.08]")) {
  fail("Catalog heading must not clip serif descenders");
}
if (!read("app/admin/catalog-list.tsx").includes("Search") || !read("app/admin/catalog-list.tsx").includes("mt-1 min-h-11 w-full")) {
  fail("Catalog search and filters must stay thumb-tall");
}
if (!read("app/admin/catalog-list.tsx").includes("min-w-0 max-w-full overflow-x-auto rounded-2xl")) {
  fail("Catalog table must shrink inside the admin frame instead of blowing the page");
}
if (read("app/admin/catalog-list.tsx").includes("block max-w-full truncate whitespace-nowrap text-xs uppercase tracking-[0.14em] text-muted")) {
  fail("Catalog filter labels must not truncate the wrapping control");
}
if (!read("app/admin/catalog-list.tsx").includes("AdminKickerLabel") || !read("app/admin/catalog-list.tsx").includes('kicker="Search"')) {
  fail("Catalog filter kickers must clip on an inner span");
}
if (
  !read("app/admin/catalog-list.tsx").includes('aria-label="Select all shown"') ||
  !read("app/admin/catalog-list.tsx").includes("inline-flex min-h-11 min-w-11 items-center justify-center")
) {
  fail("Catalog select checkboxes must stay thumb-tall");
}
if (!read("app/admin/catalog-list.tsx").includes("hidden px-4 py-3 whitespace-nowrap text-[11px] uppercase tracking-[0.12em] text-muted lg:table-cell")) {
  fail("Catalog source column must stay one KY line");
}
if (!read("app/admin/catalog-list.tsx").includes("mt-0.5 max-w-full truncate whitespace-nowrap text-[11px] text-muted sm:hidden")) {
  fail("Catalog mobile type must stay one KY line");
}
if (!read("app/admin/catalog-list.tsx").includes('className="whitespace-nowrap text-muted"')) {
  fail("Catalog Hold price must stay one KY line");
}
if (!read("components/product-status-badge.tsx").includes("whitespace-nowrap")) {
  fail("Status badges must stay one KY line");
}
if (!adminSaveBar.includes("Preview PDP") || !adminSaveBar.includes("inline-flex min-h-11 touch-manipulation")) {
  fail("Item form Preview PDP / Back must stay thumb-tall");
}
if (!adminSaveBar.includes("hover-hover:hover:opacity-90")) {
  fail("Item form Save must dim on hover pointers");
}
if (!adminSaveBar.includes("leading-[1.08]")) {
  fail("Item form Add/Edit heading must not clip serif descenders");
}
if (!adminSaveBar.includes("whitespace-nowrap text-[11px] uppercase tracking-[0.18em] text-muted")) {
  fail("Item form New/Edit kicker must stay one KY line");
}
if (!adminSaveBar.includes("max-w-full truncate whitespace-nowrap text-[11px] uppercase tracking-[0.18em] text-muted")) {
  fail("Item form New/Edit kicker must clip inside the admin frame");
}
if (adminSaveBar.includes("block max-w-full truncate whitespace-nowrap text-xs uppercase tracking-[0.14em] text-muted")) {
  fail("Item form field labels must not truncate the wrapping control");
}
if (!adminSaveBar.includes("AdminKickerLabel") || !adminSaveBar.includes('kicker="Letter"')) {
  fail("Item form Letter/Status/Fulfillment kickers must clip on an inner span");
}
if (!adminSaveBar.includes("max-w-full truncate whitespace-nowrap text-sm text-muted")) {
  fail("Item form type/status kicker must stay one KY line");
}
if (!adminSaveBar.includes("min-h-11 w-full max-w-xs") || !adminSaveBar.includes("mt-1 min-h-11 w-full")) {
  fail("Item form letter/status/fulfillment must stay thumb-tall");
}
if (!adminSaveBar.includes("admin-rename-ma") || !adminSaveBar.includes("min-h-11 touch-manipulation rounded-full bg-ink")) {
  fail("Save & change mã must stay thumb-tall");
}
if (!read("components/admin-colors.tsx").includes("Merge colors") || !read("components/admin-colors.tsx").includes("inline-flex min-h-11 touch-manipulation items-center select-none whitespace-nowrap rounded-full")) {
  fail("Admin color merge / attach must stay thumb-tall");
}
if (!read("components/admin-colors.tsx").includes("hover-hover:hover:border-gold")) {
  fail("Admin color chrome must gold-up on hover pointers only");
}
if (!read("app/admin/catalog-list.tsx").includes("hover-hover:hover:bg-blush/40")) {
  fail("Catalog rows must not stick blush after a phone tap");
}
if (!read("app/admin/console.tsx").includes("text-muted hover-hover:hover:text-ink")) {
  fail("Admin nav must not stick ink after a phone tap");
}
if (!read("components/admin-colors.tsx").includes('data-testid="admin-color-unassigned"') || !read("components/admin-colors.tsx").includes("inline-flex min-h-11 touch-manipulation items-center select-none whitespace-nowrap text-[11px] uppercase tracking-[0.12em]")) {
  fail("Admin color-tag Unassigned must stay thumb-tall");
}
if (!read("components/color-swatch.tsx").includes("inline-flex min-h-11 min-w-11 shrink-0 touch-manipulation")) {
  fail("Admin color boxes must keep a 44px hit around the small swatch");
}
if (!read("components/admin-colors.tsx").includes("h-11 w-11 cursor-pointer")) {
  fail("Admin hex pickers must stay thumb-tall");
}
if (!read("components/admin-colors.tsx").includes('data-testid="admin-add-color"') || !read("components/admin-colors.tsx").includes("inline-flex min-h-11 touch-manipulation items-center select-none whitespace-nowrap rounded-full bg-ink")) {
  fail("Admin Add color must stay thumb-tall");
}
if (!read("components/admin-colors.tsx").includes("hover-hover:hover:opacity-90")) {
  fail("Admin Add color must dim on hover pointers");
}
if (!read("components/admin-colors.tsx").includes("min-h-11 min-w-[8rem]") || !read("components/admin-colors.tsx").includes("mt-1 min-h-11 w-full")) {
  fail("Admin color merge and name fields must stay thumb-tall");
}
if (read("components/admin-colors.tsx").includes("tracking-[0.08em] text-paper")) {
  fail("Admin slide Up/Down must sit beside the thumb at 44px, not an 8px overlay");
}
if (!read("components/admin-colors.tsx").includes("truncate whitespace-nowrap bg-ink/70")) {
  fail("Color-slide Uploading overlay must stay one KY line");
}
if (!read("app/admin/editor-chrome.tsx").includes("inline-flex min-h-11 shrink-0 touch-manipulation") || !read("app/admin/editor-chrome.tsx").includes("tab-scroll")) {
  fail("Item editor section nav must stay thumb-tall and scroll");
}
if (!read("app/admin/editor-chrome.tsx").includes("min-w-0 max-w-full gap-4 overflow-x-auto tab-scroll")) {
  fail("Item editor section nav must shrink instead of blowing the form");
}
if (!read("app/admin/editor-chrome.tsx").includes("truncate whitespace-nowrap") || !read("app/admin/editor-chrome.tsx").includes("items-center whitespace-nowrap")) {
  fail("Editor KY kickers and section nav must stay one KY line");
}
if (!read("components/asia-fit.tsx").includes("hover-hover:hover:border-gold")) {
  fail("Fit cm chrome must gold-up on hover pointers only");
}
if (!read("components/asia-fit.tsx").includes("whitespace-nowrap")) {
  fail("Fit cm / Asia size chrome must stay one KY line");
}
if (!read("components/asia-fit.tsx").includes("text-paper whitespace-nowrap")) {
  fail("Asia size pills must stay one KY line");
}
if (!read("app/admin/image-fields.tsx").includes("Add URL") || !read("app/admin/image-fields.tsx").includes("inline-flex min-h-11 touch-manipulation items-center select-none whitespace-nowrap rounded-full")) {
  fail("Image Add URL / Upload must stay thumb-tall");
}
if (!read("app/admin/image-fields.tsx").includes("min-h-11 w-full rounded-lg border")) {
  fail("Image URL fields must stay thumb-tall");
}
if (!read("app/admin/image-fields.tsx").includes("truncate whitespace-nowrap")) {
  fail("Image Cover/Photo kicker must stay one KY line");
}
if (!read("app/admin/image-fields.tsx").includes("truncate whitespace-nowrap bg-ink/70")) {
  fail("Image Uploading overlay must stay one KY line");
}
if (!read("app/admin/console.tsx").includes("inline-flex min-h-11 touch-manipulation select-none items-center whitespace-nowrap text-sm")) {
  fail("Admin Back to shop must stay thumb-tall");
}
if (!read("app/admin/console.tsx").includes("min-w-0 max-w-full gap-6 overflow-x-auto tab-scroll")) {
  fail("Admin nav rail must shrink instead of blowing the console");
}
if (!read("app/admin/console.tsx").includes("min-w-0 max-w-full overflow-x-auto tab-scroll whitespace-nowrap")) {
  fail("Admin Test only kicker must stay one KY line");
}
if (!read("app/admin/console.tsx").includes("leading-[1.08]")) {
  fail("Sell ops heading must not clip serif descenders");
}
if (!read("app/admin/console.tsx").includes("toastTimers") || !read("app/admin/console.tsx").includes("clearTimeout")) {
  fail("Admin toasts must clear their hide timers on unmount");
}
if (!read("components/admin-sizes.tsx").includes("inline-flex min-h-11 touch-manipulation")) {
  fail("Admin size chips must stay thumb-tall");
}
if (!read("components/admin-sizes.tsx").includes("mt-1 min-h-11 w-full")) {
  fail("Admin Fit cm fields must stay thumb-tall");
}
if (read("components/admin-sizes.tsx").includes("block max-w-full truncate whitespace-nowrap text-xs uppercase tracking-[0.14em] text-muted")) {
  fail("Admin Fit cm labels must not truncate the wrapping control");
}
if (
  !read("components/admin-sizes.tsx").includes("block max-w-full text-xs uppercase tracking-[0.14em] text-muted") ||
  !read("components/admin-sizes.tsx").includes('span className="block max-w-full truncate whitespace-nowrap"')
) {
  fail("Admin Fit cm kickers must clip on an inner span");
}
if (!read("components/ship-draft-form.tsx").includes("copiedTimer") || !read("components/ship-draft-form.tsx").includes("touch-manipulation")) {
  fail("Ship-draft Copy mã must clear its timer and stay a tap target");
}
if (!read("components/ship-draft-form.tsx").includes("mt-1 min-h-11 w-full")) {
  fail("Ship-draft fields must stay thumb-tall");
}
if (!read("components/ship-draft-form.tsx").includes("whitespace-nowrap")) {
  fail("Ship-draft kickers and Copy mã must stay one KY line");
}
if (!gallery.includes("truncate whitespace-nowrap rounded-md px-3 py-1.5")) {
  fail("Empty gallery caption must stay one KY line");
}
if (!lightbox.includes("closeTimer") || !lightbox.includes("clearTimeout")) {
  fail("Lightbox close must clear its deferred onClose timer");
}
if (!gallery.includes('select-none" aria-hidden translate="no"')) {
  fail("Empty gallery captions must not be auto-translated");
}
if (!featured.includes("shrink-0") || !featured.includes("whitespace-nowrap")) {
  fail("Featured tabs must stay one KY line in the rail");
}
if (!featured.includes("flex-nowrap") || featured.includes("sm:flex-wrap")) {
  fail("Featured tabs must not wrap under Looks on tablet");
}
if (featured.includes("sm:overflow-visible")) {
  fail("Featured tabs must keep tab-scroll on tablet, not wrap");
}

const a01 = seed.products.find((product) => product.ma === "A01");
if (!a01) {
  fail("A01 missing");
}
const a01Reel = productGalleryReel(a01);
if (a01Reel.length !== 2 || firstReelIndexForColor(a01Reel, "xanh") !== 1) {
  fail("A01 color pick must roll to the yellow puppy slide");
}
if (firstReelIndexForColor(a01Reel, "cham-bi") >= 0) {
  fail("A01 must not roll to a foreign color id");
}
if (clampedReelIndexForColor(a01Reel, "xanh") !== 1 || clampedReelIndexForColor(a01Reel, null) !== 0) {
  fail("Card/PDP color index must clamp to this mã’s tagged slide");
}
if (firstReelIndexForColor(a01Reel, null) !== 0) {
  fail("Unset color starts at the first this-mã slide");
}
const oneCover = productGalleryReel({
  ...a01,
  images: [{ src: "/products/A01/cover.jpg", colorId: null, order: 1 }],
});
if (oneCover.length !== 1) {
  fail("One untagged cover must not clone a fake neighbor");
}
if (firstReelIndexForColor(oneCover, "kem") !== 0 || firstReelIndexForColor(oneCover, "xanh") !== 0) {
  fail("Untagged cover is shared — chips must not invent a second JPEG");
}
const k01 = seed.products.find((product) => product.ma === "K01");
if (!k01 || productGalleryReel(k01).length !== 1) {
  fail("K01 is one photo — pack 002 is the same JPEG as cover, do not clone a fake peek");
}
const h01 = seed.products.find((product) => product.ma === "H01");
if (!h01 || productGalleryReel(h01).length !== 3) {
  fail("H01 keeps three unique real photos, unbound");
}
const a02 = seed.products.find((product) => product.ma === "A02");
if (!a02 || a02.colors.some((color) => color.id === "kem" || color.id === "xanh")) {
  fail("A02 must keep its own seed colors — never borrow hub slugs");
}
if (a02.colors.map((color) => color.id).join(",") !== "ca0200") {
  fail("A02 chips are Off-white (ca0200) only — seed");
}
const a02Reel = productGalleryReel(a02);
if (a02Reel.length !== 2 || firstReelIndexForColor(a02Reel, "ca0200") !== 0) {
  fail("A02 ca0200 must roll to its own cover");
}
if (a02Reel.some((slide) => slide.src.includes("/products/A01/"))) {
  fail("A02 reel must never include A01 files");
}
if (imagesForColor(a02, "ca0200").some((image) => image.src.includes("/products/A01/"))) {
  fail("A02 must never list A01 files");
}
if (coverSrcForColor(a02, "kem") !== undefined) {
  fail("A02 Kem is not a color on this mã — coverSrcForColor must stay empty");
}
const stolenA02: Product = {
  ...a02,
  colors: [
    { id: "kem", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "xanh", hex: "#1C2A4A", name: "Xanh", note: "" },
  ],
  images: [
    { src: "/products/A01/cover.jpg", colorId: "kem", order: 1 },
    { src: "/products/A02/cover.jpg", colorId: "cham-bi", order: 2 },
  ],
};
if (imagesForColor(stolenA02, "kem").length !== 0) {
  fail("Leaked Kem on A02 must not resolve A01 hexes or photos");
}
const borrowedFolder: Product = {
  ...a02,
  images: [
    { src: "/products/A01/cover.jpg", colorId: "cham-bi", order: 1 },
    { src: "/products/A02/cover.jpg", colorId: "cham-bi", order: 2 },
  ],
};
if (imagesForColor(borrowedFolder, "cham-bi").some((image) => image.src.includes("/products/A01/"))) {
  fail("A02 cham-bi must drop A01 folder files");
}
if (imagesForColor(borrowedFolder, "cham-bi").map((image) => image.src).join(" ") !== "/products/A02/cover.jpg") {
  fail("A02 keeps its own cover only when A01 files leak into the row");
}
const twoTone: Product = {
  ...a01,
  colors: [
    { id: "kem", hex: "#F4F0E8", name: "Kem", note: "" },
    { id: "xanh", hex: "#7A8B6F", name: "Xanh", note: "" },
  ],
  images: [
    { src: "/products/A01/cover.jpg", colorId: "kem", order: 1 },
    { src: "/products/A01/shared.jpg", colorId: null, order: 2 },
    { src: "/products/A02/cover.jpg", colorId: "xanh", order: 3 },
  ],
};
const kem = imagesForColor(twoTone, "kem").map((image) => image.src);
if (kem.includes("/products/A02/cover.jpg")) {
  fail("A01 color fade must never pull A02’s cover");
}

const ctaFiles = ["components/product-card.tsx", "components/product-gallery.tsx", "components/featured-board.tsx"];
for (const rel of ctaFiles) {
  const text = read(rel);
  if (/Shop now|Add to cart|Buy with card/i.test(text)) {
    fail(`${rel} added a cart CTA`);
  }
}

console.log("motion #31 apply ok");
