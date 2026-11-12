# Indesight Town

以工作成果驅動的像素城鎮養成遊戲。完成任務獲得 XP，街區自動擴建，居民沿道路散步。

- 正式站：https://indesight-town.pages.dev/
- 部署：推送到 `main` 後，GitHub Actions 會把 `site/` 上傳到 Cloudflare Pages 專案 `indesight-town` 的 Production。

## 結構

| 路徑 | 內容 |
|---|---|
| `site/index.html` | 整個遊戲：介面、規則、等距地圖、繪圖與存檔 |
| `site/assets/` | 遊戲使用的去背美術（主建築、擴建小建築、樹、街道小物、居民動作表） |
| `art/source/` | ChatGPT 產出的原始洋紅背景圖，重新處理時使用 |
| `tools/key.py` | 洋紅去背、裁切、縮放、減色：`python3 tools/key.py 原圖 輸出.png 寬度` |
| `tools/people.py` | 角色動作表切格、腳底對齊、產生配色版本 |

## 部署所需的 GitHub Secrets

- `CLOUDFLARE_API_TOKEN`：Cloudflare API Token，權限 Account → Cloudflare Pages → Edit
- `CLOUDFLARE_ACCOUNT_ID`：Cloudflare 帳號 ID

## 存檔

進度存在瀏覽器 `localStorage`，鍵名 `indesight-town-v14`，沿用 V1.4 起的格式。改格式時要能讀舊存檔。
