export const VIEWING_COLOR_PREFIX = "Đang xem:";
export const EMPTY_GALLERY_MARK = "—";
export const COLOR_FIELD_LEGEND = "Màu / Color";
export const SIZE_FIELD_LEGEND = "Cỡ / Size";
export const ALL_PHOTOS_LABEL = "Tất cả ảnh · All photos";
export const SKIP_TO_LOOKS = "Tới looks · Skip to looks";
export const SHOP_ERROR_BODY = "Nhắn tin trên Messenger, hoặc thử lại · Message on Messenger, or try again.";

export function viewingColorLine(name: string): string {
  return `${VIEWING_COLOR_PREFIX} ${name}`;
}

export function emptyGalleryAnnouncement(colorLabel: string): string {
  return `${colorLabel}. Không có ảnh màu này trên mã này · No photos for this color on this mã.`;
}

export function messageForRealPhotos(ma: string): string {
  return `Message ${ma}`;
}

export function copyMaDone(ma: string): string {
  return `Copied ${ma}`;
}

export function copyMaDoneAria(ma: string): string {
  return `Đã sao chép ${ma} · Copied ${ma}`;
}

export function copyMaLabel(ma: string): string {
  return `Sao chép ${ma} · Copy ${ma}`;
}

export function photoIndexLabel(n: number): string {
  return `Xem ảnh ${n} · Photo ${n}`;
}

export function photoPositionLabel(index: number, total: number): string {
  if (total < 1) {
    return "";
  }
  return `Ảnh ${index} / ${total} · Photo ${index} of ${total}`;
}

export function galleryReelLabel(ma: string): string {
  return `Ảnh ${ma} · ${ma} photos`;
}

export function morePhotosLabel(count: number): string {
  return `Xem ${count} ảnh nữa · ${count} more photos`;
}

export function messageAria(ma?: string): string {
  return ma
    ? `Nhắn tin ${ma} trên Messenger · Message ${ma} on Messenger`
    : "Nhắn tin trên Messenger · Message on Messenger";
}
