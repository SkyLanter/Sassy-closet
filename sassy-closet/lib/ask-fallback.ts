import { buildCaptionVi, kindColorsLine } from "./captions";
import { KIND_CODES } from "./kinds";
import { getSubmission, listSubmissions } from "./store";
import type { AskCopy } from "./types";

export type FallbackAnswer = {
  reply: string;
  copies: AskCopy[];
};

const HARD_STOP =
  "Copy thôi — Mini Boss không Post, không Send, không Square Save, không tự đặt mã.";

export async function localAskAnswer(question: string): Promise<FallbackAnswer> {
  const q = question.trim();
  const ma = extractMa(q);
  const item = ma ? await getSubmission(ma) : null;

  if (/caption|viết caption|title/i.test(q) && item) {
    const caption = item.caption_vi || buildCaptionVi(item);
    return {
      reply: `Caption gợi ý cho ${item.ma} — copy rồi dán FB. Mini Boss không Post.`,
      copies: [{ id: "caption", label: "Copy caption", text: caption }],
    };
  }

  if (/inbox|messenger|soạn tin/i.test(q) && item) {
    const text = `Chào iu, còn ${item.ma} (${kindColorsLine(item)}) nha. Inbox mã này để giữ. Local cash/Zelle. Mini Boss không gửi hộ.`;
    return {
      reply: `Inbox draft cho ${item.ma}. ${HARD_STOP}`,
      copies: [{ id: "inbox", label: "Copy inbox", text }],
    };
  }

  if (/còn|stock|available|còn hàng/i.test(q) && item) {
    return {
      reply: `${item.ma} đang trên site (staged, not Square). Square Free mới là on-hand. ${HARD_STOP}`,
      copies: [],
    };
  }

  if (/còn|stock|available/i.test(q) && ma && !item) {
    return {
      reply: `Không thấy ${ma} trên site. Hỏi Stock / Boss — Mini Boss không invent mã.`,
      copies: [],
    };
  }

  if (/size/i.test(q)) {
    return {
      reply: "Size trên form: 2XS XS S M L XL 2XL (Asian). Không đổi sang US. Gõ mã nếu muốn xem size đã lưu.",
      copies: [],
    };
  }

  if (item) {
    return {
      reply: `${item.ma}: ${kindColorsLine(item)}${item.size ? ` · Size ${item.size}` : ""}. ${HARD_STOP}`,
      copies: [
        {
          id: "caption",
          label: "Copy caption",
          text: item.caption_vi || buildCaptionVi(item),
        },
      ],
    };
  }

  const count = (await listSubmissions()).length;
  return {
    reply: [
      "Món mới: ảnh / màu / size / giá / link tuỳ chọn → Lưu & lấy mã.",
      "Size: 2XS XS S M L XL 2XL.",
      "Màu: chip + Khác phẩy ra nhiều tên. Tìm mã: ảnh đúng file đã lưu.",
      "Hỏi còn mã / viết caption / soạn inbox — Mini Boss copy giúp, không đăng, không gửi.",
      count ? `Site đang có ${count} mã đã Lưu.` : "Chưa có mã trên site này.",
      HARD_STOP,
    ].join("\n"),
    copies: [],
  };
}

function extractMa(question: string): string | null {
  const match = question.toUpperCase().match(new RegExp(`\\b([${KIND_CODES.join("")}]\\d{2,3})\\b`));
  return match ? match[1] : null;
}
