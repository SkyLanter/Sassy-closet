/** Vercel Server Action / serverless body limit. Source: vercel.com/docs/vercel-blob/server-upload */
export const VERCEL_SERVER_ACTION_MAX_BYTES = Math.floor(4.5 * 1024 * 1024);

export function uploadOverServerActionLimit(size: number): boolean {
  return size > VERCEL_SERVER_ACTION_MAX_BYTES;
}

export function uploadTooLargeError(size: number): string {
  const mb = (size / (1024 * 1024)).toFixed(1);
  return `Image is ${mb} MB. Vercel Server Actions cap uploads at 4.5 MB — compress the JPEG. This is not a silent drop.`;
}
