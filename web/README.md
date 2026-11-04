# RenderCV Web Editor

Trình soạn CV chạy trên trình duyệt cho RenderCV: giao diện ba khung (danh
sách CV, khung soạn thảo, xem trước PDF trực tiếp), trong đó mỗi CV được
chỉnh qua bốn tab -- **CV, Design, Locale, Settings** -- mỗi tab có hai chế
độ đồng bộ hai chiều (form sinh từ schema, hoặc YAML thô), kèm bộ đổi theme,
tự động lưu, và tải PDF.

Ứng dụng được xây **trên chính core Python của repository này**, không viết
lại: `web/backend` import `rendercv` dưới dạng editable dependency và gọi
đúng pipeline mà CLI dùng, nên phần render và validate không thể lệch khỏi
core.

```
web/backend    Dịch vụ FastAPI bọc core (validate, render, schema,
               themes, lưu trữ CV, preferences)
web/frontend   Giao diện SvelteKit + TypeScript + Tailwind
```

## Yêu cầu môi trường

- **uv** (Python 3.12+) -- dùng cho mọi thứ liên quan Python; tuyệt đối
  không dùng `pip` hay gọi `python` trực tiếp. `uv` tự tạo và quản lý virtual
  environment, **không cần `python -m venv` thủ công**.
- **Node.js 20+** kèm npm.
- **just** -- chạy các gate của repository (`just check`, `just test`).
  Cài qua `winget install Casey.Just`, `brew install just`, hoặc
  `cargo install just`.

## Cài đặt

### 1. Clone kèm submodule

Repository có hai submodule, trong đó `typst_fontawesome` là **bắt buộc để
render PDF**:

```
git clone --recurse-submodules <url>
```

Nếu đã lỡ clone thường:

```
git submodule update --init --recursive
```

> Bỏ qua bước này là mọi lần render PDF đều lỗi. Core cài
> `src/rendercv/renderer/typst_fontawesome` thành một Typst package tên
> `fontawesome` (xem `renderer/pdf_png.py`); thư mục rỗng thì không tìm thấy
> `lib.typ` và quá trình biên dịch dừng lại. Kiểm tra bằng
> `git submodule status` -- không có dấu `-` ở đầu dòng là đã đủ.

### 2. Cài dependency

Ba lệnh, ở ba nơi khác nhau:

```
just sync                  # ở thư mục gốc repository -- core + gate `just check`/`just test`
```

```
cd web/backend && uv sync  # backend
```

```
cd web/frontend && npm install   # frontend
```

> Ở thư mục gốc phải dùng `just sync` (tức `uv sync --frozen --all-extras`)
> chứ không phải `uv sync` trần: bộ test của core cần các optional extras, và
> `uv sync` trần sẽ **gỡ** chúng khỏi env, khiến `just test` gãy.

Có **hai virtual environment riêng biệt**, đúng như thiết kế: `.venv` ở gốc
cho core, `web/backend/.venv` cho backend. `uv` tự tạo cả hai; bạn không cần
tự kích hoạt cái nào -- `uv run` luôn chọn đúng env theo thư mục hiện tại.

Backend phụ thuộc vào core dưới dạng *editable* path dependency, nên sửa code
core là có hiệu lực ngay với backend, không cần cài lại.

Muốn Postgres thì thêm `uv sync --extra postgres` ở `web/backend` (xem mục
[Deploy](#deploy)).

## Chạy ứng dụng

> Dùng Windows/PowerShell? [`SETUP-LOCALHOST.md`](SETUP-LOCALHOST.md) có
> đúng những lệnh này ở dạng PowerShell, kèm cách xem log và cách gỡ khi
> cổng bị chiếm.

Sao chép file mẫu biến môi trường. **Không bỏ qua bước này**: editor yêu
cầu đăng nhập, nên thiếu credentials Google là không vào được editor:

```
cd web/backend
cp .env.example .env
```

Hai tiến trình, ở hai terminal:

```
cd web/backend
uv run --env-file .env uvicorn rendercv_web.app:app --port 8000
```

> `--env-file .env` là phần dễ bỏ sót nhất. Thiếu nó thì backend không đọc
> `GOOGLE_OAUTH_CLIENT_ID`/`_SECRET` dù bạn đã điền đúng vào `.env`, và
> `/app` sẽ hiện "Sign-in is not configured" thay vì editor.

```
cd web/frontend
npm run dev
```

Mở <http://localhost:5173>. Dev server của Vite proxy `/api` sang backend ở
cổng 8000, nên **cả hai đều phải đang chạy**.

Schema database được migrate **tự động khi backend khởi động**
(`upgrade_to_head` trong lifespan của app) -- không có bước
`alembic upgrade` thủ công. Nếu không cấu hình gì, backend tạo file
`web/backend/data/rendercv_web.db` (SQLite) tương đối theo thư mục làm việc
hiện tại.

**Editor yêu cầu tài khoản.** `/api/cvs` và `/api/preferences` từ chối
người gọi chưa đăng nhập (401), và `/app` hiện màn hình đăng nhập thay vì
editor. Trang landing, `/api/themes` và `/api/schema` vẫn mở cho mọi người.

Không có bước đăng ký riêng: lần đầu và những lần sau đều bấm cùng một nút
"Sign in with Google"; server tự phân biệt bằng việc identity Google đó đã
gắn với tài khoản nào chưa. Lý do bắt buộc tài khoản: CV được lưu theo tài
khoản nên còn nguyên ở lần truy cập sau và trên máy khác, thay vì buộc vào
đúng một trình duyệt.

## Cấu hình

Danh sách đầy đủ kèm chú thích nằm trong
[`web/backend/.env.example`](backend/.env.example) -- copy thành `.env` rồi
điền. `.env` đã được gitignore; file mẫu thì không, nên đừng bao giờ đặt giá
trị thật vào đó.


| Biến môi trường | Mặc định | Ghi chú |
| --- | --- | --- |
| `RENDERCV_WEB_DATABASE_URL` | `sqlite:///./data/rendercv_web.db` | Nhận mọi URL kiểu SQLAlchemy. Postgres chạy được mà không cần sửa code. |
| `RENDERCV_WEB_SECRET` | *(giá trị dev không an toàn)* | Dùng để ký cookie phiên. **Bắt buộc phải đặt trước khi deploy** -- xem mục [Deploy](#deploy). |
| `RENDERCV_WEB_HTTPS` | *(tắt)* | Đặt `1` khi phục vụ qua HTTPS để cookie phiên có cờ `Secure`. |
| `RENDERCV_WEB_ALLOWED_ORIGINS` | `http://localhost:5173` | Origin được phép gọi API, ngăn cách bằng dấu phẩy. Chỉ cần khi frontend khác origin với API. |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` / `_REDIRECT_URI` | *(chưa đặt)* | **Bắt buộc.** Chưa đặt thì không ai vào được editor -- `/app` báo thẳng là deployment thiếu cấu hình. |

## Kiểm thử

Mỗi tầng có gate riêng. Tất cả phải xanh trước khi mở PR.

**Core** (chạy từ thư mục gốc repository):

```
just check
just test
```

**Backend:**

```
cd web/backend
uv run pytest -q
```

**Frontend** (kiểm tra kiểu, unit test, build production):

```
cd web/frontend
npm run check
npm run test
npm run build
```

**End-to-end (Playwright).** Một lệnh, không cần chuẩn bị gì:

```
cd web/frontend
npm run test:e2e
```

Playwright tự dựng **cả hai** server của riêng nó: backend ở cổng 8100 với
một database dùng-một-lần trong thư mục temp, và frontend ở cổng 5199. Dev
server 5173/8000 bạn đang mở không bị đụng tới, và bộ test **không thể** ghi
vào database thật của bạn.

> Trước đây bước này bắt bạn tự mở backend kèm `RENDERCV_WEB_DATABASE_URL`
> trỏ vào database tạm. Quên biến đó một lần là CV test ghi thẳng vào dữ
> liệu phát triển -- nên việc đó nay do Playwright làm.

Vì editor yêu cầu tài khoản, `e2e/global-setup.ts` tạo sẵn một *pool* tài
khoản trong database tạm (chạy code repository thật qua
`e2e/seedAccount.py`), và mỗi test nhận một tài khoản riêng qua
`e2e/fixtures.ts`. Không có endpoint đăng nhập dành cho test nào được thêm
vào server -- một endpoint như vậy là đường vòng qua xác thực, chỉ cách một
lỗi cấu hình là ai cũng gọi được.

Bộ test chạy `workers: 1` một cách có chủ đích: backend chỉ là một tiến
trình uvicorn duy nhất, và các lần render Typst nặng CPU sẽ làm nghẽn chính
event loop của nó khi chạy song song.

## Tuỳ chọn: xem trước phía client (WASM)

Bình thường bản xem trước do backend render, và đó vẫn là bộ render chuẩn.
Ngoài ra còn một đường chạy hoàn toàn phía client: Pyodide chạy wheel
rendercv để sinh mã nguồn Typst, rồi typst.ts biên dịch ra PDF ngay trong
trình duyệt, không gọi `/api/render` lần nào.

Tính năng này **mặc định tắt** và không tốn gì cho tới khi được bật. Muốn
thử, build assets một lần (~30 MB, đổ vào `static/wasm/` đã được gitignore):

```
cd web/frontend
npm run build:wasm-assets
```

Rồi bật cờ trong console của trình duyệt và tải lại trang:

```
localStorage.setItem('rendercv.wasmPreview', 'true')
```

Giới hạn đã biết: chỉ có font của theme classic, bản thân Pyodide được tải
từ CDN jsdelivr, và vài dependency Python thuần nhỏ được lấy từ PyPI lúc
chạy. Khởi động nguội mất khoảng 17-20 giây; các lần render sau khi đã nóng
máy dưới một giây.

## Đăng nhập Google (bắt buộc)

Editor chỉ mở cho người đã đăng nhập, nên đây không còn là tuỳ chọn: chưa
cấu hình OAuth client thì không ai dùng được editor.

Khi chưa cấu hình, backend báo `provider_available: false`, landing page ẩn
nút đăng nhập, và `/app` hiện thẳng "Sign-in is not configured" kèm tên hai
biến còn thiếu -- không có nút chết, và người vận hành không phải đoán.

Tạo OAuth client ở [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
chọn *Create credentials* → *OAuth client ID* → *Web application*, rồi khai
báo **Authorized redirect URI** đúng bằng địa chỉ mà trình duyệt sẽ quay về:

| Môi trường | Redirect URI |
| --- | --- |
| Dev | `http://localhost:5173/api/auth/google/callback` |
| Deploy | `https://<tên-miền-của-bạn>/api/auth/google/callback` |

URI phải khớp **từng ký tự**, kể cả `https` và dấu `/` cuối. Sai một chút là
Google trả `redirect_uri_mismatch`.

Rồi đặt biến môi trường cho backend:

```
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=https://<tên-miền-của-bạn>/api/auth/google/callback
```

App mới tạo nằm ở chế độ **Testing**. Google chặn mọi email ngoài danh
sách *Test users* ngay trên màn hình của Google -- request không bao giờ tới
server này, nên không có gì phía code xử lý được. Chủ project là ngoại lệ:
họ luôn đăng nhập được kể cả khi danh sách trống.

Cho người khác vào bằng cách thêm email của họ: *Google Auth Platform* →
**Audience** → *Test users* → **Add users**. Danh sách chứa 100 địa chỉ và
có hiệu lực ngay.

**Publish (chuyển sang *In production*) cần một domain công khai**, nên nó
không phải bước làm được từ máy local. Google đòi *homepage url* và
*privacy policy url* hợp lệ trước khi cho chuyển, và hai URL đó phải thuộc
một domain khai trong *Authorized domains* -- `localhost` không dùng được.
Để publish thì phải deploy trước; xem [Deploy](#deploy).

Khi tới lúc đó, **gỡ logo trong *Branding* trước khi publish**: Google bắt
app có logo phải qua verification, trừ khi đang ở Testing. Bản thân ba scope
app xin (`openid email profile`) đều non-sensitive nên không cần
verification.

### Phiên và tài khoản hoạt động thế nào

| Tình huống | Điều xảy ra |
| --- | --- |
| Đăng nhập lần đầu | Tạo tài khoản luôn, không có form đăng ký riêng |
| Trình duyệt còn CV ẩn danh từ bản deploy cũ | CV đó **được gộp vào tài khoản**, không mất gì |
| Đang đăng nhập rồi đăng nhập bằng **tài khoản Google khác** | Chuyển tài khoản sạch sẽ: tài khoản cũ **không bị đụng tới**, CV của nó vẫn thuộc về nó |
| Đăng xuất | **Thoát trên mọi thiết bị**, không chỉ trình duyệt hiện tại |

Hai dòng cuối đáng chú ý:

- Trường hợp đổi tài khoản từng là một lỗi nghiêm trọng — tài khoản thứ nhất
  bị ghi đè hoặc xoá hẳn, CV rơi sang người mới. Đã sửa và có test hồi quy
  canh giữ.
- Đăng xuất thoát mọi thiết bị vì một tài khoản chỉ có một `session_token`.
  Đây là lựa chọn có chủ đích: giữa "bị thoát bất ngờ ở máy khác" và "phiên
  không thu hồi được", cái đầu tốn một cú click, cái sau mất tài khoản.
  Muốn thoát theo từng thiết bị thì cần thêm bảng `sessions` riêng.

## Deploy

> Cần hướng dẫn từng bước (tạo OAuth client, chọn Postgres, chạy migration,
> kiểm chứng)? Xem
> [`docs/runbooks/enable-google-sign-in-and-postgres.md`](../docs/runbooks/enable-google-sign-in-and-postgres.md).
> Mục dưới đây là phần tra cứu.

### Một origin duy nhất, không phải hai

**Frontend và API phải nằm chung một origin.** Đây không phải sở thích đóng
gói mà là ràng buộc kỹ thuật: cookie phiên đặt `SameSite=Lax`, nên trình
duyệt **không gửi cookie** trong request `fetch` sang site khác. Tách frontend
và API ra hai host thì đăng nhập vẫn thành công rồi mất phiên ngay ở request
kế tiếp — và không cấu hình CORS nào cứu được, vì CORS cho request đi qua còn
`SameSite` giữ cookie lại. Không có lỗi CORS nào hiện ra để lần dấu vết.

Lưu ý `vercel.app` nằm trong Public Suffix List, nên `a.vercel.app` và
`b.vercel.app` cũng là **hai site khác nhau** — để cả hai trên Vercel không
thoát được.

Vì vậy [`web/Dockerfile`](Dockerfile) đóng gói cả hai vào một image: frontend
build ra file tĩnh, backend phục vụ chúng cùng lúc với `/api`.

```
git submodule update --init --recursive
docker build -f web/Dockerfile -t rendercv-web .
docker run -p 8000:8000 -e RENDERCV_WEB_SECRET=... rendercv-web
```

**Build context là thư mục gốc repository, không phải `web/`** — backend phụ
thuộc core dưới dạng editable path dependency nên cần cả cây nguồn của core,
và cần submodule `typst_fontawesome` để render PDF.

Đừng nhầm với `Dockerfile` ở thư mục gốc: đó là image của **CLI** RenderCV
thượng nguồn, việc khác hẳn.

### Render

[`render.yaml`](../render.yaml) là blueprint dựng sẵn service. Trên Render
chọn *New → Blueprint*, trỏ vào repository này.

Render tự sinh `RENDERCV_WEB_SECRET`. `RENDERCV_WEB_DATABASE_URL` và ba biến
Google được đánh dấu `sync: false` nên Render sẽ hỏi lúc deploy, thay vì nằm
trong file công khai.

Database là **Supabase**, không phải Postgres của Render: bản free của
Render hết hạn sau khoảng một tháng rồi bị xoá cùng dữ liệu (deployment đầu
tiên đã sập vì vậy, 2026-10-19). Lấy chuỗi kết nối theo mục
[Postgres](#postgres) bên dưới.

Sau lần deploy đầu, Render cấp hostname — lúc đó mới điền được
`GOOGLE_OAUTH_REDIRECT_URI` và khai đúng URI đó trong Google Cloud Console:

```
https://<ten-service>.onrender.com/api/auth/google/callback
```

> Gói free của Render **ngủ sau 15 phút không có request**, và lần đánh thức
> đầu mất vài chục giây. Với đồ án demo thì chấp nhận được, nhưng đừng ngạc
> nhiên khi lần mở đầu tiên chậm.

### Xem trước phía client (WASM) không có trong image

Image cố ý **không chạy** `npm run build:wasm-assets`. Nó gom khoảng 30MB
Pyodide, font và một wasm binary của Typst cho bộ render phía client — thứ
mặc định đang tắt — và bản thân script cần `uv build`, tức phải nhét cả
toolchain Python vào tầng Node để tạo ra thứ không ai bật.

Hệ quả: bật cờ WASM trên một deployment build theo cách này sẽ ra một bộ
render không có asset để tải. Muốn dùng thì phải thêm bước build đó vào
Dockerfile.

### Biến môi trường

| Biến | Bắt buộc | Ghi chú |
| --- | --- | --- |
| `RENDERCV_WEB_SECRET` | **Có** | Chuỗi ngẫu nhiên đủ dài, giữ ngoài mã nguồn. Xem cảnh báo bên dưới. |
| `RENDERCV_WEB_HTTPS` | **Có** (khi chạy HTTPS) | Đặt `1` để cookie phiên được đánh dấu `Secure`. Không đặt thì cookie đi qua mạng ở dạng đọc được. |
| `RENDERCV_WEB_DATABASE_URL` | Nên có | Chuỗi kết nối Postgres. Không đặt thì rơi về SQLite theo file, sẽ mất dữ liệu mỗi lần container khởi động lại. |
| `RENDERCV_WEB_FRONTEND_DIR` | Có (khi deploy) | Thư mục chứa bản build frontend để backend phục vụ. Image tự đặt sẵn. Bỏ trống thì backend chỉ phục vụ API và mọi trang trả 404 — đúng cho môi trường dev, nơi Vite lo phần frontend. |
| `RENDERCV_WEB_ALLOWED_ORIGINS` | Hầu như không | Chỉ dùng khi frontend khác origin với API — cấu hình **không chạy được**, xem mục [Một origin duy nhất](#một-origin-duy-nhất-không-phải-hai). |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` | **Có** | Thiếu thì không ai vào được editor. |
| `GOOGLE_OAUTH_REDIRECT_URI` | **Có** (khi deploy) | `https://<domain>/api/auth/google/callback`, khớp từng ký tự với khai báo trong Google Cloud Console. |

> **`RENDERCV_WEB_SECRET` là thứ dễ quên nhất và hậu quả nặng nhất.** Giá
> trị dự phòng là một chuỗi hardcode nằm trong repository công khai -- ai
> cũng có thể giả mạo cookie phiên có chữ ký hợp lệ và đọc CV của người
> khác. Backend chỉ ghi cảnh báo vào log chứ không chặn, nên không có gì
> nhắc bạn ngoài dòng log đó.

### Postgres

Cài kèm driver -- **đây là bước hay bị bỏ sót**, thiếu nó backend chết ngay
lúc khởi động:

```
uv sync --extra postgres
```

Chuỗi kết nối dán thẳng từ nhà cung cấp là dùng được. Cả ba dạng dưới đây
đều chạy, vì backend tự chuẩn hoá về driver đã cài:

```
postgres://...              (Railway, Heroku)
postgresql://...            (Neon, Supabase)
postgresql+psycopg://...    (dạng SQLAlchemy đầy đủ)
```

Không cần chạy migration bằng tay: backend tự nâng schema lên bản mới nhất
lúc khởi động.

**Với Supabase, dùng chuỗi Session pooler** (nút *Connect* → *Session
pooler*), dạng `postgresql://postgres.<project-ref>:<mật-khẩu>@aws-0-<region>.pooler.supabase.com:5432/postgres`:

- *Direct connection* (`db.<project-ref>.supabase.co`) chỉ có IPv6 ở gói
  free, Render không kết nối tới được.
- *Transaction pooler* (cổng `6543`) làm hỏng prepared statement mà
  psycopg 3 dùng; lỗi chỉ xuất hiện sau vài truy vấn.
- Mật khẩu có ký tự đặc biệt (`@`, `#`, `/`…) phải được URL-encode.
- Chọn region gần service (`rendercv-web` ở Oregon → *West US (Oregon)*).
- Project free của Supabase **bị tạm dừng sau 7 ngày không có hoạt động**.
  Dữ liệu vẫn còn, bấm *Restore* trong dashboard Supabase là chạy lại; trong
  lúc tạm dừng, backend chết lúc khởi động giống hệt khi mất database.

### CORS

Deploy theo cách mô tả ở [Một origin duy
nhất](#một-origin-duy-nhất-không-phải-hai) thì **bỏ qua mục này** — không có
request cross-origin nào để cho phép, và `RENDERCV_WEB_ALLOWED_ORIGINS` để
trống.

`RENDERCV_WEB_ALLOWED_ORIGINS` chỉ có nghĩa khi frontend nằm khác origin với
API. Nhưng cấu hình đó **không chạy được** với cookie hiện tại, vì lý do đã
nêu ở mục trên: CORS cho request đi qua, `SameSite=Lax` vẫn giữ cookie lại.
Khai biến này rồi tưởng xong là kiểu sai mất nhiều thời gian nhất, vì không
có thông báo lỗi nào chỉ ra nguyên nhân.

Muốn thật sự tách origin thì phải đổi cookie sang `SameSite=None; Secure` —
một thay đổi bảo mật cần cân nhắc riêng, chưa làm.

### Tệp xác minh của Google — đừng xoá

`web/frontend/static/googlecdc32a5d8f95119a.html` không phải rác. Google
Search Console tải nó về ở gốc website để xác nhận tên miền này là của
mình, và trang đồng ý OAuth chỉ được phép mang địa chỉ trang chủ cùng
privacy policy sau khi việc xác nhận đó thành công.

Đây là loại tệp rất dễ bị dọn nhầm: **không có dòng code nào trong ứng dụng
đọc nó**, nên xoá đi thì mọi thứ ở đây vẫn chạy y nguyên. Hậu quả rơi ở chỗ
khác — Search Console lặng lẽ huỷ xác minh, và Google có thể gỡ branding
khỏi màn hình đăng nhập, không có thông báo nào trong repo giải thích tại
sao.

Vì vậy nó được một e2e test canh (`web/frontend/e2e/landing.spec.ts`, mục
"Google site verification"): test gọi đúng địa chỉ Google gọi và đối chiếu
nội dung với chính tên tệp. Xoá tệp là test đỏ.

Nội dung phải giữ **nguyên từng byte** như Google phát ra. Đừng thêm chú
thích vào bên trong tệp — lời giải thích thuộc về chỗ này.

## Đọc tiếp ở đâu

- `docs/plans/completed/cv-editor-web-app.md` -- kế hoạch thực thi, kèm bằng
  chứng kiểm chứng của từng phase.
- `graphify-out/GRAPH_REPORT.md` -- bản đồ sinh tự động về cách core và các
  tầng web kết nối với nhau.
- `CLAUDE.md` ở thư mục gốc -- quy ước code, áp dụng cho cả Python trong
  `web/backend` lẫn core.
