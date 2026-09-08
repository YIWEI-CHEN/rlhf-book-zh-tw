# 增修版規格

本文件記錄已確定的命名與來源規則；它不是發布公告。

## 命名

| 項目 | 值 |
|---|---|
| 預定 GitHub repo | `YIWEI-CHEN/rlhf-book-zhtw-edition` |
| README 與 Pages 標題 | `RLHF - 從人類回饋中強化學習 (增修版)` |
| 中文稱呼 | 正體中文 |
| 首次發布 tag | `v0.1`（不是 `v0.1.0`） |
| PDF 檔名 | `rlhf-book-zh-tw-v0.1.pdf` |
| EPUB 檔名 | `rlhf-book-zh-tw-v0.1.epub` |
| HTML 閱讀網址 | <https://yiwei-chen.github.io/rlhf-book-zh-tw/> |

repo slug 使用 `zhtw`，下載檔名使用 `zh-tw`，兩者是刻意採用不同命名。

## 來源與驗證狀態

- 原書作者：Nathan Lambert 與貢獻者；原始 repo：[natolambert/rlhf-book](https://github.com/natolambert/rlhf-book)。
- 正體中文正文與互動閱讀網站基底：[ai-twinkle/rlhf-book-zh-tw](https://github.com/ai-twinkle/rlhf-book-zh-tw)，由 Twinkle AI Community 翻譯與製作。
- 翻譯 repo 基底 commit：`41834be9275d000a864e275a7347e7e13941536e`（2026-07-10 02:08:36 UTC，即洛杉磯時間 2026-07-09）。
- 納入的既有增修內容基底：`2ebf945ff63c377750f5ddd3d7351dfcd6c0d7eb`，包含引用、文獻預覽、Markdown 顯示與公式連結修正；這是本次命名修改前的內容快照，不是最終發布 SHA。
- ai-twinkle README 宣告的英文版本日期：`2026-07-01`。
- 英文版本候選：[`book/v0.10`](https://github.com/natolambert/rlhf-book/releases/tag/book/v0.10)，已核對 tag 對應 `854a344dc316f4c147280a3448c31cd97d953b6d`，發布日為 2026-06-28。
- 翻譯與候選版本的對應狀態：**未確認**。發布日期接近不等於內容完全相同；精確英文來源 SHA 不得猜填。

正式發布時，另外記錄該次正體中文內容與官方程式碼的完整 commit SHA。書稿、程式碼與本增修版各自有版本，不以同一個版本號混用。

## README 與授權

- 新 repo 的自撰入口說明使用上方指定標題，來源說明使用「正體中文」。
- 原書及 `code/` 中的英文 `README.md` 保持原文；正體中文說明另存 `README.zh-TW.md`。若原書根目錄 README 與增修版入口衝突，將上游原文原樣保存在明確的 upstream 目錄，記錄來源 SHA，不以翻譯覆寫。
- 清楚區分原書作者、原翻譯社群與增修維護者 Yi-Wei Chen，不暗示官方背書。
- 書稿與翻譯沿用 CC BY-NC-SA 4.0；保留現有 LICENSE。匯入程式碼時保留 MIT、Apache 2.0 等各模組的原授權、copyright 及 notices，不重新統一授權。
- Pages 首頁與各章頁尾標示原書及 ai-twinkle 出處；既有閱讀網址不因新 repo 名稱而改動。

## 發布順序

1. 以現有正體中文內容及已完成修正為主，先建立 PDF 匯出；不要求先追平最新英文版。
2. 加入 EPUB 匯出，驗證公式、目錄、文獻及跨章跳轉。
3. 匯入固定版本的官方程式碼，另加正體中文 README，保留英文原文與授權。
4. `v0.1` 發布時，PDF 與 EPUB 使用同一份內容快照；記錄 HTML 部署來源 SHA，說明是否與下載版一致。

目前僅有 HTML 閱讀與上述規格；新 repo、PDF／EPUB 匯出、程式碼匯入與 `v0.1` release 尚未建立。
