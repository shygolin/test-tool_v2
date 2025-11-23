# Streamlit Cloud 上的 Google Sheets 設置指南

## ✅ 第一步：建立 Google 服務帳戶（詳細步驟）

這個步驟只需要做一次。

### 1️⃣ 訪問 Google Cloud Console
- 打開 https://console.cloud.google.com/
- 用你的 Google 帳戶登入

### 2️⃣ 建立新項目
- 在頁面頂部，點擊「專案選擇器」下拉菜單
- 點擊「新建專案」按鈕
- 輸入專案名稱（例如：「登分工具」）
- 點擊「建立」

### 3️⃣ 啟用 Google Sheets API
- 在左側導覽菜單，點擊「API 和服務」→「API 程式庫」
- 在搜尋框搜尋「Google Sheets API」
- 點擊結果，然後按「啟用」按鈕

### 4️⃣ 建立服務帳戶
- 在左側導覽菜單，點擊「API 和服務」→「認證」
- 點擊「建立認證」→「服務帳戶」
- 填寫帳戶名稱（例如：「登分工具」）
- 點擊「建立並繼續」
- 跳過可選步驟，點擊「完成」

### 5️⃣ 下載 JSON 金鑰
- 在「服務帳戶」列表中，點擊剛才建立的帳戶
- 點擊「金鑰」標籤
- 點擊「新增金鑰」→「建立新金鑰」
- 選擇 JSON 格式，點擊「建立」
- **重要：** JSON 文件會自動下載，請妥善保管！

---

## ✅ 第二步：在 Streamlit Cloud 中設置密鑰

### 1️⃣ 打開 Streamlit Cloud 應用設置
- 在你的應用頁面，找到右上角的「⋯」菜單
- 點擊「Settings」（設置）

### 2️⃣ 添加密鑰
- 點擊左側「Secrets」（密鑰）
- 複製以下內容到文字框：

```
google_sheets_credentials = """
{JSON 文件的完整內容}
"""
```

使用說明：
1. 用文字編輯器打開從 Google 下載的 JSON 文件
2. 複製文件的所有內容（從第一個 `{` 到最後的 `}` ）
3. 將複製的內容粘貼到上面的 `{JSON 文件的完整內容}` 位置
4. 點擊「Save」（保存）

---

## ✅ 第三步：分享 Google Sheet 給服務帳戶

### 1️⃣ 找到服務帳戶的電子郵件
- 打開你下載的 JSON 文件（用文字編輯器）
- 找到 `"client_email"` 字段
- 複製電子郵件地址（看起來像：`my-service@my-project.iam.gserviceaccount.com`）

### 2️⃣ 分享 Google Sheet
- 打開你要使用的 Google Sheet
- 點擊右上角「分享」按鈕
- 在輸入框中貼上服務帳戶的電子郵件地址
- 選擇「編輯者」權限
- 點擊「分享」
- 可以關閉「通知服務帳戶」的提示

### 3️⃣ 完成！
- 回到此應用並刷新頁面
- 現在你可以開始上傳成績了！

---

## 常見問題排查

✓ 確保服務帳戶已啟用 Google Sheets API
✓ 確保 JSON 密鑰正確貼在 Streamlit Cloud 的 Secrets 中
✓ 確保 Google Sheet 已分享給服務帳戶的電子郵件地址
✓ 如果還是無法上傳，嘗試刷新應用頁面
