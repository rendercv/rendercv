# rendercv-web-frontend

Giao diện SvelteKit + TypeScript + Tailwind của RenderCV Web Editor: bố cục
ba khung, bốn tab tài liệu với đồng bộ hai chiều form ↔ YAML, bộ đổi theme,
tự động lưu, và bản xem trước PDF trực tiếp.

Nó giao tiếp với `web/backend` qua `/api` (được proxy sang cổng 8000 khi
chạy dev), và tuỳ chọn render hoàn toàn trong trình duyệt bằng engine WASM
phía client nằm ở `src/lib/wasm/`.

**Hướng dẫn cài đặt, cách chạy và cách kiểm thử được viết một lần cho cả hai
nửa của ứng dụng, tại [`../README.md`](../README.md).** Hãy bắt đầu từ đó.

Tra nhanh các script trong workspace này:

| Lệnh | Tác dụng |
| --- | --- |
| `npm run dev` | Dev server ở cổng 5173 (cần backend chạy ở 8000). |
| `npm run check` | Kiểm tra kiểu bằng `svelte-check`. |
| `npm run test` | Chạy unit test Vitest một lượt. |
| `npm run build` | Build production. |
| `npm run test:e2e` | Playwright. **Cần backend chạy trên database dùng-một-lần** -- xem README chung ở thư mục `web/`. |
| `npm run build:wasm-assets` | Build ~30 MB assets cho bản xem trước WASM (tuỳ chọn) vào `static/wasm/` đã gitignore. |
