# dudu_outfits_store

服飾購物網站，使用 Django 與 MySQL。網站提供商品瀏覽、會員、購物車、結帳、優惠與會員制度；商品、訂單與行銷活動由 Django 管理後台維護。

## 正式環境

- 網站：https://web-production-fa3f02.up.railway.app/
- 管理後台：https://web-production-fa3f02.up.railway.app/admin/
- 部署平台：Railway
- 原始碼：GitHub `huangk781-netizen/beautyoutfiitstore` 的 `main` 分支

Railway 網址是平台產生的公開網址。網站顯示名稱已是 `dudu_outfits_store`；若要使用自己的網址，請在 Railway 的 `web` 服務設定自訂網域。

## 主要功能

- 商品分類、商品資訊、最多 10 張商品圖片、尺寸、顏色、SKU 與庫存管理
- 會員註冊、帳密登入、登出、會員中心與訂單紀錄
- 購物車數量調整、庫存檢查與結帳
- ATM/銀行轉帳、貨到付款與超商取貨；結帳時固定加收店到店運費 NT$60
- 優惠券、滿額折扣、滿額贈品與會員點數折抵
- 訂單狀態、退貨申請、物流追蹤碼與銷售儀表板
- 管理後台的會員、商品、訂單、優惠券、行銷活動與公告管理
- 已設定 Google 登入的程式整合；必須另外設定 Google OAuth 與 Django Site/Social App 才能使用

## 目前限制

- 使用者忘記密碼頁面尚未實作。
- 預設 Email 是開發用的 console backend，不會真的寄信。要寄出出貨通知或會員公告，必須設定 SMTP 服務。
- 結帳目前建立訂單，不包含信用卡、第三方支付或自動收款驗證。
- Railway 的本機檔案系統不是永久儲存空間。商品圖片暫時存放在應用程式內，重新部署後可能遺失；正式營運前應改用 Cloudinary、Amazon S3 或 Cloudflare R2。

## 技術組成

- Python 3.13 / Django 6.1
- MySQL（Railway 正式環境）與 SQLite（本機預設）
- Gunicorn、WhiteNoise、django-environ、django-allauth
- Tailwind CSS 3
- Railway Railpack 部署

## 本機啟動

### 1. 準備環境

安裝 Python 3.13 與 Node.js，然後在專案根目錄執行：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
```

### 2. 建立本機設定

將 `.env.example` 複製成 `.env`，本機可先使用以下最小設定：

```env
SECRET_KEY=replace-this-with-a-local-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

不要將 `.env`、資料庫密碼或 SMTP API Key 提交到 Git。

### 3. 初始化資料庫與靜態檔案

```powershell
python manage.py migrate
npm run build:css
python manage.py runserver
```

開啟 http://127.0.0.1:8000/。

開發 CSS 時，可在另一個終端機執行：

```powershell
npm run watch:css
```

### 4. 建立本機管理員

```powershell
python manage.py createsuperuser
```

依畫面設定自己的帳號、Email 與密碼，然後到 http://127.0.0.1:8000/admin/ 登入。

專案不再使用或保證任何預設管理員帳密。

## Railway 部署

### 服務結構

Railway 專案有兩個服務：

- `web`：Django 網站，連到 GitHub `main`，公開網址在此服務的 `Settings -> Networking`。
- `MySQL`：資料庫，只提供給 `web` 服務的內部連線。不要開啟 MySQL 的 `Public Access`，除非有明確需求並了解資安風險。

`railway.json` 會在每次部署時自動執行：

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

因此新增 migration 後只要推送 GitHub，Railway 就會自動更新資料庫。

### web 服務必填 Variables

在 Railway 的 `web -> Variables` 設定以下變數：

| 變數 | 正式環境範例 | 用途 |
| --- | --- | --- |
| `SECRET_KEY` | 長且隨機的字串 | Django 加密與 Session 安全 |
| `DEBUG` | `False` | 正式環境不可開啟除錯頁 |
| `MYSQL_URL` | Railway MySQL 提供的參照變數 | Django 連 MySQL；不要手動公開此值 |
| `ALLOWED_HOSTS` | `web-production-fa3f02.up.railway.app` | 允許 Django 接受此網域 |
| `CSRF_TRUSTED_ORIGINS` | `https://web-production-fa3f02.up.railway.app` | 讓登入、註冊與後台表單可安全送出 |
| `BANK_TRANSFER_BANK_NAME` | `國泰世華銀行` | ATM/銀行匯款訂單完成頁顯示的銀行名稱 |
| `BANK_TRANSFER_BANK_CODE` | `013` | ATM/銀行匯款訂單完成頁顯示的銀行代碼 |
| `BANK_TRANSFER_ACCOUNT_NUMBER` | 你的收款帳號 | ATM/銀行匯款訂單完成頁顯示的收款帳號 |

若使用自訂網域，將它也加到 `ALLOWED_HOSTS` 與 `CSRF_TRUSTED_ORIGINS`。多個值以逗號分隔。

收款帳號只能設定在 Railway Variables，不要寫進 `.env` 範例、原始碼或 GitHub；網站只會在會員完成 ATM/銀行匯款訂單後顯示這些資料。

### 部署流程

```powershell
git add .
git commit -m "Describe the change"
git push origin main
```

在 Railway 的 `web -> Deployments` 確認最新部署顯示 `Success`。若失敗，開啟該部署的 `Logs`，查看最下方的 Django `Traceback`。

## 正式環境管理員

管理後台網址：

```text
https://web-production-fa3f02.up.railway.app/admin/
```

在 Railway 建立或新增管理員：

1. 從專案畫面點選 `web` 服務，不是 `MySQL`。
2. 開啟 `Console`。
3. 執行：

```bash
python manage.py createsuperuser
```

4. 依畫面輸入新的帳號、Email 與密碼。

密碼輸入時終端機不會顯示任何字元，這是正常的安全行為。請妥善保存密碼；不要使用或文件化共用預設密碼。

手機可使用同一個 `/admin/` 網址登入。請用 Chrome 或 Safari，允許此網站的 Cookie；不要使用可能封鎖 Cookie 的內嵌預覽視窗。

## 後台日常操作

建議建立商品的順序：

1. 在 `商品分類` 新增分類。
2. 在 `商品` 新增商品名稱、分類、價格、描述與商品主圖；在下方的 `附加商品圖片` 新增其他圖片。主圖與附加圖片合計最多 10 張，`顯示順序` 數字較小者會先顯示。
3. 在商品頁的 `商品規格` 新增尺寸、顏色、SKU 與庫存。
4. 確認商品的 `is_active` 已啟用，再到前台檢查。

訂單處理：

- 管理後台的 `訂單` 可查看取貨資訊、付款方式、物流方式、店到店運費與明細。
- 訂單設為「已出貨」時，必須填寫物流追蹤碼。
- 訂單變成「已完成」時，會計算會員點數與會員等級。
- 會員可在訂單完成後申請退貨；管理員可在後台處理退貨狀態。

## Email 與通知

網站會在訂單成立與訂單設為「已出貨」時寄送 Email。正式環境未設定 SMTP 時，Email 內容只會輸出到伺服器日誌。

若使用 Gmail，先在 Google 帳號開啟兩步驟驗證，建立專供此網站使用的「應用程式密碼」。再於 Railway `web -> Variables` 加入：

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-store-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-google-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-store-email@gmail.com
```

`EMAIL_HOST_PASSWORD` 必須是 Google 應用程式密碼，不是 Gmail 的一般登入密碼。帳密與 API Key 都只能存放在 Railway Variables，不可寫入程式碼或 Git。

## 重要網址

| 頁面 | 網址 |
| --- | --- |
| 首頁 | `/` |
| 商品列表 | `/products/` |
| 購物車 | `/cart/` |
| 結帳 | `/checkout/` |
| 訂單列表 | `/orders/` |
| 會員登入 | `/accounts/login/` |
| 會員註冊 | `/accounts/register/` |
| 會員中心 | `/accounts/profile/` |
| 管理後台 | `/admin/` |
| 銷售儀表板（管理員） | `/dashboard/` |

## 專案結構

```text
accounts/     會員、登入、會員等級與點數
cart/         Session 購物車
config/       Django 設定與全站路由
marketing/    優惠券、滿額活動與會員公告
orders/       結帳、訂單、退貨與銷售儀表板
products/     分類、商品與商品規格
static_src/   Tailwind CSS 原始檔
static/       編譯後靜態資源
templates/    Django 模板
railway.json  Railway 建置與啟動設定
```

## 疑難排解

### 管理後台或登入頁顯示 403 CSRF

確認 Railway `web` 服務已設定正確的 `ALLOWED_HOSTS` 與 `CSRF_TRUSTED_ORIGINS`，並使用正常瀏覽器重新開啟網站。清除該網站 Cookie 後再試一次也能排除舊 Cookie 問題。

### 註冊或結帳顯示 500 Server Error

到 Railway `web -> Deployments -> 最新部署 -> Logs`，重新操作一次後，將 `Traceback` 的完整內容作為除錯依據。只看 Request Log 的 HTTP 500 無法判斷真正原因。

### MySQL Console 顯示 `python: command not found`

這表示目前開的是 `MySQL` 的 Console。要執行 `python manage.py ...` 必須切換到 `web` 服務的 Console。

### 商品圖片在重新部署後消失

這是 Railway 暫存檔案系統的正常行為。改用外部物件儲存服務後，再將 Django 的 media storage 設定改成該服務。

## 上線前檢查

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` 為新的隨機值
- [ ] `MYSQL_URL` 由 Railway MySQL 服務提供
- [ ] `ALLOWED_HOSTS` 與 `CSRF_TRUSTED_ORIGINS` 包含正式網域
- [ ] 已建立自己的管理員，且沒有共用或預設密碼
- [ ] 手機與電腦都能開啟前台、登入頁與 `/admin/`
- [ ] 已新增至少一個商品分類、商品與有庫存的商品規格
- [ ] 已測試註冊、登入、購物車、結帳與管理後台訂單操作
- [ ] 若要寄信，已設定 SMTP 並完成實際寄信測試
- [ ] 商品圖片已改用永久儲存服務，或已接受重新部署後可能遺失的風險
