# 開發環境設定與啟動說明

## 環境資訊
- Python 3.13
- Django 6.1（安裝於專案內的虛擬環境 `venv/`）
- 資料庫：預設 SQLite（開發階段），檔案位置 `db.sqlite3`；設定 `DATABASE_URL` 或 Railway MySQL 的 `MYSQL_URL` 環境變數即可切換 MySQL（不用改程式碼，見下方「部署到 Railway」）
- 專案設定：`config/settings.py`（機密資訊已改為讀環境變數，見下方「環境變數」）
- Apps：`accounts`（會員/註冊登入）、`products`（商品）、`orders`（訂單/結帳）、`cart`（購物車，session 儲存，不需要資料表）、`marketing`（優惠券/滿額活動/會員公告）
- GitHub：https://github.com/huangk781-netizen/beautyoutfiitstore （分支 `main`，本機 git 身份只在這個 repo 內設定，沒有動全域設定）

## 管理員帳號（Django Admin）
- 網址：http://127.0.0.1:8000/admin/
- 帳號：`admin`
- 密碼：`admin12345`

> 建議登入後至後台右上角「修改密碼」自行更改，此密碼僅供開發測試使用，勿用於正式環境。

## 啟動網站

```bash
cd D:\clothing
venv\Scripts\activate
python manage.py runserver
```

啟動後開啟瀏覽器至 http://127.0.0.1:8000/admin/ 登入即可管理資料。

停止伺服器：在終端機視窗按 `Ctrl+C`。

## 常用指令

```bash
# 修改 models.py 後，產生 migration 檔
python manage.py makemigrations

# 套用 migration 到資料庫
python manage.py migrate

# 開啟 Django shell（互動式測試 Model）
python manage.py shell

# 建立另一個管理員帳號
python manage.py createsuperuser
```

## 目前進度（第一階段：核心購物流程）

### Model 與後台
- [x] 虛擬環境、Django、Pillow 安裝
- [x] 專案與 accounts / products / orders 三個 app
- [x] Model：Member（tier、points）、Category / Product / ProductVariant、Order（付款方式、狀態機）/ OrderItem
- [x] 註冊 Django Admin 後台
- [x] Migration 已套用、管理員帳號已建立
- [x] 內部驗收：後台實測建立分類/商品/多規格、會員（tier/points）、訂單（付款方式、明細、狀態切換）皆正常，規格唯一性限制正確擋下重複資料

### 前台：商品瀏覽
- [x] Tailwind CSS build 流程（package.json / tailwind.config.js，韓系清新配色）
- [x] 商品列表頁 `/products/`（分類篩選、上架商品格狀排列、mobile-first）
- [x] 商品詳細頁 `/products/<id>/`（尺寸/顏色按鈕選規格、庫存為 0 自動標示已售完並不可選）

### 前台：購物車
- [x] Session 購物車（`cart` app，未登入也可使用，數量自動累加、上限依庫存 clamp）
- [x] 商品詳細頁「加入購物車」按鈕串接實際功能
- [x] 購物車頁面 `/cart/`（+/− 調整數量、移除、總金額、前往結帳按鈕佔位）
- [x] Navbar 購物車圖示 + 數量徽章

### 前台：會員與結帳
- [x] 會員註冊 `/accounts/register/`（帳號、Email、手機、密碼）、登入 `/accounts/login/`、登出
- [x] 結帳前必須登入，未登入點「前往結帳」會導向登入頁並帶 `?next=`，登入/註冊完成後自動導回結帳頁、購物車內容保留
- [x] 結帳頁 `/checkout/`（唯讀購物車摘要、收件資訊、物流方式/付款方式用按鈕選、送出訂單建立 Order+OrderItem、扣庫存、清空購物車）
- [x] 結帳完成頁：依付款方式顯示匯款假帳號或 COD 提示
- [x] 訂單查詢 `/orders/`（僅顯示自己的訂單）與訂單詳情 `/orders/<id>/`
- [x] 商品詳細頁加入購物車前可選數量（+/− ，clamp 在庫存上限）
- [x] 結帳選「超商取貨」時會多顯示門市名稱輸入框（必填，選宅配到家則隱藏）
- [x] 全站 header 加上明確的「回首頁」按鈕（每頁都有，base.html 統一處理）
- [ ] LINE/IG、電子發票、報表等後續階段功能

### 視覺與品牌
- [x] 配色改為粉色系（primary `#FBE4EC` / secondary `#F6CFDD` / accent `#D67D9C` / neutral `#5C4550` / base `#FFF8FA`，設定於 `tailwind.config.js`）
- [x] 賣場名稱改為 `beauty_outfits_store`（頁面標題、Navbar 品牌、footer 皆已更新）

## 目前進度（第二階段：付款出貨流程完整化）
- [x] 後台訂單管理：狀態下拉可切換七種狀態；狀態改為「已出貨」時強制要求填託運單號（`OrderAdminForm` 驗證）；批次動作「標記為已付款」「標記為已退貨」；後台列表用顏色標籤顯示狀態
- [x] 會員端訂單列表/詳情頁：狀態用顏色標籤區分（待付款橘/已付款藍/備貨中紫/已出貨藍/已完成綠/退貨中紅/已退貨灰），已出貨會顯示託運單號
- [x] 退換貨流程：`Order.return_reason` 欄位；已完成的訂單可在詳情頁按「申請退貨」填寫原因，狀態變「退貨中」；後台確認收到退貨後標記為「已退貨」；退款人工處理，系統只記錄狀態
- [x] 訂單編輯限制：會員端本來就沒有任何可以修改收件資訊或取消訂單的功能，所以「已出貨後不能改」這件事天然成立，不需要額外加限制

## 目前進度（第三階段：會員與行銷）
- [x] 會員等級/點數：`accounts.LoyaltySettings`（後台可調整升等門檻、給點/折抵比例，全站只有一筆設定）；訂單狀態變「已完成」時自動依實付金額給點、依累計已完成訂單金額自動升等（只會往上升，不會因退貨自動降級）
- [x] 會員中心 `/accounts/profile/`：顯示目前等級、點數、累計消費金額、距離下一等級還差多少
- [x] Google 登入（django-allauth）：架構已完整串接，登入/註冊頁會自動偵測有沒有設定 Google 憑證，沒設定就不顯示按鈕（不會噴錯）；要啟用需自己申請 Google OAuth 憑證，見下方「Google 登入設定」
- [x] Facebook / LINE 登入：架構上沿用同一套 allauth 機制，之後要加時只要裝對應 provider（LINE 目前 allauth 官方沒有內建 provider，需另外找套件或自接）+ 在後台新增 Social application 即可，不用改架構
- [x] 優惠券／折扣碼：`marketing.Coupon`（代碼、固定金額/百分比、最低消費、限首購、有效期間、使用次數上限）；結帳頁可輸入代碼按「套用」預覽折扣，正式送出訂單時一併套用並自動累計使用次數，超過上限或已過期會擋下（不影響其餘結帳流程，只是不折扣）
- [x] 滿額活動：`marketing.PromotionRule`（滿 X 元折 Y 元 / 滿 X 元贈送指定商品）；結帳頁自動偵測購物車金額是否達標並顯示，折抵金額自動加總；滿額贈品目前是「記錄在訂單上提醒出貨時要附上」，不會自動出貨（因為贈品要選哪個規格出貨仍需人工判斷）

## 目前進度（第四階段：優化與上線準備）
- [x] Email 通知：訂單狀態變「已出貨」時自動寄信給會員（開發階段用 console backend，信件內容會印在跑 `runserver` 的終端機視窗，不會真的寄出）；後台「會員公告」（`marketing.Announcement`）可選會員等級（或全部會員）建立公告，用批次動作「發送通知」逐一寄信（不會讓會員互相看到彼此 Email）
- [x] 銷售儀表板 `/dashboard/`（僅限後台管理員，一般會員/訪客會被導去登入頁）：本月銷售額、本月訂單數、近 7 天每日銷售額、熱銷商品前 10 名
- [x] 部署準備：機密資訊全部改讀環境變數（`django-environ`）、`requirements.txt`、`Procfile`、`runtime.txt`、`whitenoise` 處理正式環境靜態檔案、MySQL 連線已備妥（設定 `MYSQL_URL` 或 `DATABASE_URL`）
- [ ] 商品評論：使用者決定不需要這項功能，跳過
- [ ] LINE 官方帳號、IG 自動回覆：使用者決定等網站正式上線、有實際訂單量後再評估

## 前台開發相關指令

```bash
# 修改 tailwind.config.js 或 templates 後，重新編譯 CSS
npm run build:css

# 開發時持續監看並自動重新編譯
npm run watch:css
```

## Google 登入設定（要實際能用需要你自己做這幾步）

1. 到 [Google Cloud Console](https://console.cloud.google.com/) 建立專案 → 「API 和服務」→「憑證」→ 建立「OAuth 用戶端 ID」，應用程式類型選「網頁應用程式」
2. 「已授權的重新導向 URI」填：`http://127.0.0.1:8000/social/google/login/callback/`（正式上線後要換成正式網域的同樣路徑）
3. 建立後會拿到一組 Client ID 和 Client Secret
4. 到後台 http://127.0.0.1:8000/admin/socialaccount/socialapp/ 新增一筆：Provider 選 Google，填入 Client ID / Secret，Sites 選現在的網站
5. 回登入頁 http://127.0.0.1:8000/accounts/login/，應該就會出現「使用 Google 帳號登入」按鈕

在還沒設定憑證之前，登入/註冊頁不會顯示 Google 按鈕（設計成優雅隱藏，不會讓頁面壞掉）。

## 環境變數

專案的機密資訊（SECRET_KEY、資料庫連線等）已經改成讀環境變數，不再寫死在程式碼裡。

- **本機開發**：不用做任何事，程式碼裡有安全的開發用預設值，沒有 `.env` 檔案也能正常跑。
- **想自訂本機設定**：複製 `.env.example` 另存成 `.env`，改裡面的值即可（`.env` 已加入 `.gitignore`，不會被提交）。
- **正式環境**：不需要 `.env` 檔案，直接在 PaaS 平台（例如 Railway）的環境變數頁面設定即可，程式會自動讀到。

主要變數說明都寫在 [.env.example](.env.example) 裡，包含 `SECRET_KEY`、`DEBUG`、`ALLOWED_HOSTS`、`DATABASE_URL` / `MYSQL_URL`、Email 相關設定。

## 部署到 Railway（PaaS）前的準備

**專案端已經準備好的東西：**
- `requirements.txt`：所有 Python 套件清單（`pip freeze` 產生）
- `Procfile`：告訴 Railway 怎麼啟動網站，內容是「先跑 migration → 收集靜態檔案 → 用 gunicorn 啟動」
- `runtime.txt`：指定 Python 版本（3.13）
- `whitenoise`：讓 Django 自己就能在正式環境提供 CSS/JS 靜態檔案，不用額外設定 Nginx 或 CDN
- 資料庫設定已經是讀 `DATABASE_URL` 或 `MYSQL_URL` 環境變數，Railway 開一個 MySQL 服務後可使用 `MYSQL_URL`（或你手動複製貼上到 Django 服務的環境變數也可以）

**已經完成：** 專案已經 `git init` 並推上 GitHub：https://github.com/huangk781-netizen/beautyoutfiitstore （分支 `main`）

**你需要自己做的事：**
1. 申請 [Railway](https://railway.app/) 帳號（可以用 GitHub 登入）
2. 在 Railway 建立新專案，選「Deploy from GitHub repo」，選這個 repo
3. 再加一個 MySQL 服務（Railway 的「Add Database」裡選 MySQL）
4. 在 Django 服務的「Variables」頁籤設定環境變數，至少要有：
   - `SECRET_KEY`：換一組新的隨機字串（不要用開發環境那組）
   - `DEBUG`：`False`
   - `ALLOWED_HOSTS`：Railway 會給你一個 `xxx.up.railway.app` 網域，填進去（之後綁自訂網域再加上去）
   - `MYSQL_URL` 或 `DATABASE_URL`：從 MySQL 服務的 Variables 頁籤複製 `MYSQL_URL` 到 Django 服務；若你想沿用 `DATABASE_URL` 名稱，也可以把同一串值貼成 `DATABASE_URL`
   - Email 相關（如果要真的寄信，見 `.env.example` 裡的 SendGrid 範例；不設的話會維持 console backend，正式環境不會真的寄信但也不會出錯）
6. 部署後，商品圖片這類使用者上傳的檔案要注意：Railway 的檔案系統每次重新部署會清空，正式環境建議之後改接雲端儲存（例如 S3），這個階段先不用處理，只是提醒你別太早上傳重要商品圖。

## 已知待辦（下一步處理）
- 商品卡片/詳細頁圖片目前需透過後台 `/admin/products/product/` 手動上傳 `商品圖片` 欄位，未上傳時會顯示「尚無圖片」佔位樣式。
- 購物車是 session-based，登出會清空購物車（Django `logout()` 會重置 session）。目前結帳前才要求登入，所以正常購物流程不受影響；但如果之後想讓使用者「先登入再逛街」，登出清空購物車這件事要注意。
- 匯款帳號目前是假資料（陽春銀行 700 / 123-456-789012），正式上線前要換成真的帳戶。
- 目前沒有「重新核對庫存後自動調整購物車」的 UI 提示，只有結帳送出時如果庫存不足會擋下並顯示錯誤訊息，請回購物車手動調整。
- 會員等級目前只會自動往上升，不會因為退貨而自動降級；點數也是訂單完成時才發放，退貨不會自動收回已發的點數（這兩塊如果要做「回收」邏輯，之後可以再加）。
- 滿額贈品只會記錄在訂單的「贈品」欄位提醒出貨時要附上，不會自動幫贈品建立訂單明細或扣贈品庫存。
- Facebook / LINE 登入還沒真的接，架構已經是 allauth 可以直接擴充的樣子。
