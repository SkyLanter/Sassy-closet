# Intake color detect (client)

Drop-in for the live Next.js intake (`lib/colors-client.ts`).

- Canvas / RGBA only — no vision APIs
- Auto-fills Màu chips (no Suggest button)
- Ignores studio couch / paper / wood-floor backs; scores the center garment blob
- Cream knits → **Kem** (not backdrop Trắng/Be); red knits → **Đỏ**

```bash
cd sassy-closet
npm install
npm test
npm run prove
```
