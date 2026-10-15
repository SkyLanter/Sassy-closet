/**
 * Copy for the intake form.
 * Rewrites failure text only. Does not mint a mã or suggest the next free code.
 */

const CNY_AMOUNT = /^\d+(?:\.\d+)?$/;

const BLOCK_CODES = ["held", "never-list", "s06-lock", "reused", "duplicate"] as const;

type BlockCode = (typeof BLOCK_CODES)[number];

const SAVE_BLOCK =
  /^(Không lưu|Không mint) ([A-Z]\d{2,3}) \((held|never-list|s06-lock|reused|duplicate)\)\.$/;

export const INTAKE_SAVE_FAILED = "Chưa lưu được mã. Không có gì được ghi. Thử lại.";

const LOOKUP_MISS = "Không tìm thấy mã này. Kiểm tra chữ và số rồi mở lại.";

export type CostCnyWarning = {
  kind: "blank" | "garbled";
  text: string;
};

export function costCnyWarning(costCny: string): CostCnyWarning | null {
  const stripped = costCny.trim();
  if (stripped === "") {
    return {
      kind: "blank",
      text: "Chưa có giá ¥. Vẫn lưu được, nhưng mã sẽ thiếu giá vốn. Điền ¥ nếu đã có giá.",
    };
  }
  if (!CNY_AMOUNT.test(stripped)) {
    return {
      kind: "garbled",
      text: "Giá ¥ chưa phải một số (ví dụ 87.23). Vẫn lưu được, nhưng giá này không được đọc là ¥.",
    };
  }
  return null;
}

export function explainIntakeFailure(message: string): string {
  const match = SAVE_BLOCK.exec(message);
  if (match) {
    const minted = match[1] === "Không mint";
    const ma = match[2] ?? "";
    const code = match[3] ?? "";
    if (isBlockCode(code)) return blockSentence(code, ma, minted);
  }
  if (
    !message.trim() ||
    message === "Chưa lưu được, thử lại nha." ||
    message === "Chưa nhận được mã. Thử lại nha 🥺"
  ) {
    return INTAKE_SAVE_FAILED;
  }
  if (message === "Không tìm thấy mã này 🥺") return LOOKUP_MISS;
  return message;
}

function isBlockCode(value: string): value is BlockCode {
  return (BLOCK_CODES as readonly string[]).includes(value);
}

function blockSentence(code: BlockCode, ma: string, minted: boolean): string {
  const lead = minted ? `Chưa lấy được mã mới ${ma}.` : `Chưa lưu được ${ma}.`;
  switch (code) {
    case "held":
      return `${lead} Mã này đang được giữ lại, chưa cho lên shop. Không có gì được ghi.`;
    case "never-list":
      return `${lead} Mã này không được dùng. Không có gì được ghi.`;
    case "s06-lock":
      return `${lead} Giá bán S06 chỉ được $25 hoặc để trống. Giá khác không được ghi.`;
    case "reused":
      return `${lead} Mã này đã được dùng. Form không gộp vào mã cũ. Không có gì được ghi.`;
    case "duplicate":
      return `${lead} Mã này đã có. Form không gộp vào mã cũ. Không có gì được ghi.`;
    default: {
      const neverCode: never = code;
      return neverCode;
    }
  }
}
