# Chạy và test app trên máy local

Hướng dẫn đi từ lúc clone repository đến lúc **mọi bộ test xanh**. Viết cho
Windows + PowerShell, là môi trường dự án đang phát triển.

> **PowerShell 5.1 không hiểu `&&`.** Chép lệnh nhiều dòng kiểu bash vào đây
> sẽ báo `The token '&&' is not a valid statement separator in this version`.
> Mọi lệnh dưới đây chạy **từng dòng một**.

Ba tài liệu, đừng nhầm lẫn:

| File | Dùng khi |
| --- | --- |
| **`local_setup.md`** (file này) | Lần đầu dựng máy, và khi cần chạy đủ bộ test |
| [`web/SETUP-LOCALHOST.md`](web/SETUP-LOCALHOST.md) | Lệnh dùng hằng ngày, xem log, gỡ khi cổng bị chiếm |
| [`web/README.md`](web/README.md) | Kiến trúc, cấu hình, deploy |

## 0. Cần có sẵn

| Công cụ | Kiểm tra |
| --- | --- |
| `git` | `git --version` |
| `uv` | `uv --version` |
| `just` | `just --version` |
| Node.js 20+ | `node --version` |

Thiếu `just` thì cài theo hướng dẫn ở <https://github.com/casey/just#installation>.

## 1. Clone kèm submodule

```powershell
git clone --recurse-submodules <url-repository>
```

Lỡ clone thường rồi thì bổ sung:

```powershell
git submodule update --init --recursive
```

> **Bỏ qua bước này là mọi lần render PDF đều lỗi.** Core cài
> `src/rendercv/renderer/typst_fontawesome` thành Typst package tên
> `fontawesome`; thư mục rỗng thì không tìm thấy `lib.typ` và Typst dừng
> biên dịch. Kiểm tra bằng `git submodule status` — không có dấu `-` ở đầu
> dòng là đủ.

## 2. Cài dependency — ba lệnh, ba nơi

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041"
```

```powershell
just sync
```

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\backend"
```

```powershell
uv sync
```

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\frontend"
```

```powershell
npm install
```

> **Ở thư mục gốc phải dùng `just sync`, không phải `uv sync` trần.**
> `just sync` là `uv sync --frozen --all-extras`. Bộ test của core cần các
> optional extras, còn `uv sync` trần sẽ **gỡ** chúng khỏi env và `just test`
> gãy ngay sau đó. (Đây là lỗi tôi từng mắc khi chạy thử chính tài liệu mình
> viết.)

Có **hai virtual environment riêng biệt**, đúng thiết kế: `.venv` ở gốc cho
core, `web/backend/.venv` cho backend. Không cần tự activate cái nào — `uv run`
tự chọn đúng env theo thư mục hiện tại. Backend phụ thuộc core dưới dạng
*editable path dependency*, nên sửa code core có hiệu lực ngay, không cài lại.

## 3. Cấu hình `.env`

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\backend"
```

```powershell
Copy-Item .env.example .env
```

Mở `.env` và điền hai giá trị:

```
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
```

> **Bước này bắt buộc nếu muốn mở editor bằng trình duyệt.** Editor chỉ mở
> cho tài khoản đã đăng nhập: `/api/cvs` và `/api/preferences` trả 401 cho
> người gọi chưa đăng nhập, và `/app` hiện màn hình đăng nhập thay vì editor.
> Thiếu credentials thì `/app` báo thẳng "Sign-in is not configured".
>
> **Chỉ chạy test thì không cần bước này** — mục 6 dưới đây giải thích vì sao.

Lấy credentials ở
[Google Cloud Console](https://console.cloud.google.com/apis/credentials) →
*Create credentials* → *OAuth client ID* → *Web application*, rồi khai báo
**Authorized redirect URI** đúng từng ký tự:

```
http://localhost:5173/api/auth/google/callback
```

Cổng là **5173** (frontend), không phải 8000 — trình duyệt phải quay về đúng
origin đang giữ cookie phiên. Từng bước chi tiết:
[`docs/runbooks/enable-google-sign-in-and-postgres.md`](docs/runbooks/enable-google-sign-in-and-postgres.md).

> **Muốn người khác đăng nhập được thì thêm email của họ vào *Test users*.**
> Google Cloud Console → *Google Auth Platform* → **Audience** → mục *Test
> users* → **Add users** → gõ địa chỉ Gmail → Save. Có hiệu lực ngay, không
> phải chờ duyệt.
>
> "Test users" nghe như phải đi tìm người thử nghiệm, nhưng thực ra chỉ là
> **danh sách email được phép đăng nhập**. Người được thêm không nhận thông
> báo gì và không phải làm gì cả. Danh sách chứa tối đa 100 địa chỉ, thừa
> cho một dự án môn học.
>
> Bạn — chủ project — luôn đăng nhập được kể cả khi danh sách trống. Nên
> muốn nghiệm thu thật thì phải dùng một tài khoản Google khác; tài khoản
> chính của bạn vào được trong mọi trường hợp nên không chứng minh được gì.
>
> Ai **không** có trong danh sách sẽ bị Google chặn ngay trên màn hình của
> Google — app của mình không hề nhận được request nào, nên không có cách
> nào xử lý phía code.

`.env` đã được gitignore. `.env.example` thì không — đừng bao giờ đặt giá trị
thật vào file mẫu.

## 4. Chạy app — hai terminal

### Terminal 1 — Backend (cổng 8000)

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\backend"
```

```powershell
uv run --env-file .env uvicorn rendercv_web.app:app --port 8000
```

> **`--env-file .env` là phần dễ quên nhất.** Thiếu nó, backend không đọc
> `GOOGLE_OAUTH_CLIENT_ID`/`_SECRET` dù bạn đã điền đúng, và `/app` sẽ hiện
> "Sign-in is not configured" — trông y như tính năng bị hỏng.

Schema database migrate **tự động khi backend khởi động**, không có bước
`alembic upgrade` thủ công. Không cấu hình gì thì backend tạo file SQLite ở
`web/backend/data/rendercv_web.db`.

### Terminal 2 — Frontend (cổng 5173)

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\frontend"
```

```powershell
npm run dev
```

Mở <http://localhost:5173>. Trang chủ là landing page, mở được cho mọi người.
Editor ở <http://localhost:5173/app> và yêu cầu đăng nhập.

Vite proxy `/api` sang cổng 8000, nên **thiếu backend là editor không tải
được gì**.

## 5. Kiểm tra nhanh xem đã lên chưa

```powershell
Invoke-RestMethod http://localhost:8000/api/auth/me
```

`provider_available: true` nghĩa là backend đã đọc được credentials Google.
`false` là chưa — quay lại mục 3 và 4.

Xác nhận đúng app của mình đang giữ cổng 8000 (quan trọng hơn bạn tưởng, một
app khác cũng có thể đang chiếm cổng đó):

```powershell
(Invoke-RestMethod http://localhost:8000/openapi.json).info.title
```

Phải ra `RenderCV Web Editor API`.

## 6. Chạy test — năm cổng, tất cả phải xanh

Chạy được **không cần** app đang chạy, và **không cần** credentials Google.

### 6.1 Core — lint và type

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041"
```

```powershell
just check
```

Kỳ vọng: mọi hook `Passed`. Lỗi format thì chạy `just format` rồi `just check`
lại.

### 6.2 Core — test

```powershell
just test
```

Kỳ vọng: **1540 passed, 2 skipped**. Hai test skip trên Windows là đúng dự
kiến (`chmod` và schema generation khác nhau trên Windows), không phải lỗi.

### 6.3 Backend web

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\backend"
```

```powershell
uv run --frozen pytest -q
```

Kỳ vọng: **109 passed**.

### 6.4 Frontend — type và unit

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\frontend"
```

```powershell
npm run check
```

Kỳ vọng: `0 ERRORS 0 WARNINGS`.

```powershell
npm run test
```

Kỳ vọng: **300 passed**.

### 6.5 End-to-end (Playwright)

Một lệnh, không cần chuẩn bị gì:

```powershell
npm run test:e2e
```

Kỳ vọng: **46 passed**, khoảng 2–3 phút.

Playwright tự dựng **cả hai** server của riêng nó: backend ở **cổng 8100** với
database dùng-một-lần trong `%TEMP%`, và frontend ở **cổng 5199**. Dev server
5173/8000 bạn đang mở không bị đụng tới, và bộ test **không thể** ghi vào
database thật.

> Trước đây bước này bắt bạn tự mở backend kèm `RENDERCV_WEB_DATABASE_URL`
> trỏ vào database tạm rồi nhớ gỡ biến đi. Quên một lần là CV test ghi thẳng
> vào dữ liệu thật — nên việc đó nay do Playwright làm.

Vì editor bắt buộc đăng nhập, `e2e/global-setup.ts` tạo sẵn một pool tài khoản
trong database tạm (chạy code repository thật qua `e2e/seedAccount.py`), và
mỗi test nhận một tài khoản riêng qua `e2e/fixtures.ts`. Không có endpoint
đăng nhập dành riêng cho test nào được thêm vào server — một endpoint như vậy
là đường vòng qua xác thực, chỉ cách một lỗi cấu hình là ai cũng gọi được.

Xem báo cáo chi tiết khi có test đỏ:

```powershell
npx playwright show-report
```

### Chạy tất cả một lượt

Dán từng khối, theo thứ tự:

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041"; just check; just test
```

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\backend"; uv run --frozen pytest -q
```

```powershell
Set-Location "C:\AI Thuc Chien\PROJECT\rendercv_P-041\web\frontend"; npm run check; npm run test; npm run test:e2e
```

> Dùng `;` chứ không phải `&&`. Khác biệt: `;` chạy lệnh sau **kể cả khi**
> lệnh trước hỏng, nên nhớ đọc kỹ output từng phần chứ đừng chỉ nhìn dòng
> cuối.

## Lỗi hay gặp

| Triệu chứng | Nguyên nhân |
| --- | --- |
| `The token '&&' is not a valid statement separator` | Chép lệnh bash vào PowerShell — dùng `;` hoặc chạy từng dòng |
| `just test` gãy hàng loạt sau khi vừa cài | Đã chạy `uv sync` trần ở thư mục gốc; chạy lại `just sync` |
| Render PDF lỗi tìm `lib.typ` | Chưa init submodule — xem mục 1 |
| `/app` hiện "Sign-in is not configured" | Backend chạy thiếu `--env-file .env`, hoặc `.env` chưa có credentials |
| `401 invalid_client` **ngay lập tức** | Sai Client ID |
| Chọn được tài khoản Google **rồi** mới lỗi | Sai Client secret |
| `redirect_uri_mismatch` | Redirect URI khai trong Console không khớp từng ký tự |
| Đăng nhập bị Google chặn quyền truy cập | Email chưa nằm trong danh sách *Test users* |
| `GET /api/cvs 401` trong log | Chưa đăng nhập — đúng thiết kế, không phải bug |
| Editor không tải được CV nào | Backend chưa chạy, hoặc cổng 8000 đang bị app khác chiếm |

Cổng bị chiếm, xem log, hoặc gỡ tiến trình mồ côi: xem
[`web/SETUP-LOCALHOST.md`](web/SETUP-LOCALHOST.md).

## Dọn dẹp

Dừng mọi tiến trình Python của **riêng dự án này** (lọc theo đường dẫn, không
đụng Python khác trên máy):

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*rendercv_P-041*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

Frontend thì `Ctrl+C` ở terminal của nó là đủ.
