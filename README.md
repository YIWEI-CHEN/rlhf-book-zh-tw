# RLHF - 從人類回饋中強化學習 (增修版)

> **非官方正體中文增修版（Unofficial Traditional Chinese Revised Edition）**
>
> 原書《[Reinforcement Learning from Human Feedback](https://rlhfbook.com)》由 **Nathan Lambert 與貢獻者**撰寫，原始專案為 [natolambert/rlhf-book](https://github.com/natolambert/rlhf-book)。
>
> 本版的正體中文正文與互動閱讀網站，以 **Twinkle AI Community** 的 [ai-twinkle/rlhf-book-zh-tw](https://github.com/ai-twinkle/rlhf-book-zh-tw) 為基礎，由 **[Yi-Wei Chen](https://yiwei-chen.github.io/)** 加入引用連結、文獻懸停預覽、公式跳轉與 Markdown 顯示修正，並非重新獨立翻譯，也不是原作者或 Twinkle AI 的官方增修版。
>
> 書稿與翻譯沿用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant) 授權，保留原作者與翻譯社群署名，不得作商業用途。支持原作者請購買[實體書](https://rlhfbook.com)。

**📖 增修版線上閱讀：<https://yiwei-chen.github.io/rlhf-book-zh-tw/>**

原正體中文翻譯與互動網站：[Twinkle AI Community 線上版](https://apps.twinkleai.tw/rlhf-book-zh-tw/)。

## 增修版規格與來源版本

增修版的新 repo 名稱確定為 `rlhf-book-zhtw-edition`；此 fork 保留既有 Pages 網址與回饋上游的用途。第一個預定發布版本為 **`v0.1`**，PDF 與 EPUB 的預定檔名分別為：

- `rlhf-book-zh-tw-v0.1.pdf`
- `rlhf-book-zh-tw-v0.1.epub`

目前提供 HTML 閱讀；PDF／EPUB 匯出及官方程式碼整合尚未完成，不代表已有可下載的 `v0.1` release。

正體中文基底固定為 ai-twinkle 的 [`41834be`](https://github.com/ai-twinkle/rlhf-book-zh-tw/commit/41834be9275d000a864e275a7347e7e13941536e)。其 README 宣告翻譯依據為 **2026-07-01 版**；可能對應原書 [`book/v0.10`](https://github.com/natolambert/rlhf-book/releases/tag/book/v0.10)（2026-06-28 發布，commit `854a344dc316f4c147280a3448c31cd97d953b6d`），但**精確的英文原稿 commit 尚未確認**，因此不宣稱已驗證為 v0.10 或已同步最新英文版。

匯入原書與 `code/` 時保留其原英文 `README.md`，正體中文說明另存為 `README.zh-TW.md`，不覆寫原文。書稿與各程式碼模組保留各自的授權、署名及 notices；不以書稿授權取代程式碼授權。完整命名與版本規格見 [EDITION.md](EDITION.md)。

原翻譯專案為每一章配備一個**互動實驗**，本版保留這些實驗，讓讀者能動手操作該章的核心概念——從 Bradley-Terry 偏好機率、PPO 裁剪目標、GRPO 群組優勢，到 DPO 損失曲面與前向／反向 KL 的收斂行為。

## 互動實驗一覽

| 章節 | 實驗 |
|---|---|
| 第 1 章 導論 | RLHF 三步驟互動管線 |
| 第 2 章 RLHF 簡史 | RLHF 發展互動時間軸 |
| 第 3 章 訓練總覽 | 溫控器 RL 模擬器 |
| 第 4 章 指令微調 | 聊天模板建構器（ChatML／Zephyr／Tülu＋損失遮罩） |
| 第 5 章 獎勵模型 | Bradley-Terry 獎勵模型探索器 |
| 第 6 章 強化學習 | PPO 裁剪目標／GRPO 群組優勢遊樂場 |
| 第 7 章 推理與推論時擴展 | pass@k vs 多數決模擬 |
| 第 8 章 直接對齊演算法 | DPO 損失探索器 |
| 第 9 章 拒絕採樣 | 拒絕採樣與 Best-of-N 模擬器 |
| 第 10 章 偏好的本質 | 偏好聚合悖論（Condorcet 循環） |
| 第 11 章 偏好資料 | 當一次偏好標註員（偏誤陷阱體驗） |
| 第 12 章 合成資料與蒸餾 | 知識蒸餾軟標籤實驗室 |
| 第 13 章 工具使用 | 工具呼叫流程模擬器 |
| 第 14 章 過度最佳化 | 獎勵過度最佳化模擬（Goodhart 定律） |
| 第 15 章 正則化 | KL 散度探索器（前向 vs 反向） |
| 第 16 章 評估 | 評估雜訊模擬器 |
| 第 17 章 模型性格 | Persona 向量調音台 |
| 附錄 A／B／C | 詞彙抽認卡／話多平衡體驗器／評測變異查核器 |

## 目錄結構

```
├── content/                     # 逐章翻譯的獨立 Markdown（17 章 + 3 附錄 + 參考文獻）
├── webapp/                      # 互動式網站（純靜態、完全離線可用）
│   ├── index.html               # 目錄首頁
│   ├── chapters/*.html          # 每章一頁（內嵌翻譯內容）
│   └── assets/                  # 樣式、渲染器、互動元件、插圖、本地函式庫
└── build.py                     # 建置腳本：content/*.md → webapp 頁面
```

## 本地使用

```bash
cd webapp && python3 -m http.server 8642   # 瀏覽 http://localhost:8642
```

修改 `content/*.md` 或新增 `webapp/assets/widgets/*.js` 後重新執行 `python3 build.py`。

## 翻譯慣例

- 專有名詞第一次出現採「中文（English）」，常用縮寫（RLHF、PPO、DPO、SFT…）保留英文
- 數學式以 LaTeX 轉錄，公式編號沿用原書（`\tag{n}`）
- 文獻引用標記 [N] 對應 `content/bibliography.md`（保留原文）
- 程式碼區塊保留原文，註解翻譯

發現翻譯問題歡迎開 issue 或 PR。

---

## About (English)

This is an **unofficial Traditional Chinese (zh-TW) revised edition**, maintained by [Yi-Wei Chen](https://yiwei-chen.github.io/), of *[Reinforcement Learning from Human Feedback](https://rlhfbook.com)* by Nathan Lambert and contributors ([original repository](https://github.com/natolambert/rlhf-book)). The translation and interactive website are based on the [Twinkle AI Community project](https://github.com/ai-twinkle/rlhf-book-zh-tw), with additional citation, equation-link, and Markdown-rendering fixes. This is not an official edition from the original author or Twinkle AI.

The translation source declares a 2026-07-01 edition. `book/v0.10` is a possible upstream baseline, not a verified match. The planned revised-edition repository is `rlhf-book-zhtw-edition`, starting at `v0.1`; PDF/EPUB downloads and upstream code integration are not yet available. Imported English READMEs will be preserved, with separate `README.zh-TW.md` documentation.

The **interactive labs** from the Twinkle AI project are retained, including the Bradley-Terry explorer, PPO clipping / GRPO group-advantage playground, DPO loss explorer, and forward/reverse KL visualizer.

**Read this revised edition online: <https://yiwei-chen.github.io/rlhf-book-zh-tw/>**

[Original Twinkle AI reading site](https://apps.twinkleai.tw/rlhf-book-zh-tw/).

Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), same as the original chapters. Non-commercial; full attribution to the original author. Please support the author by purchasing the [print edition](https://rlhfbook.com).

## Citation

Please cite the original book:

```bibtex
@book{rlhf2026lambert,
  author       = {Nathan Lambert},
  title        = {Reinforcement Learning from Human Feedback},
  year         = {2026},
  publisher    = {Online},
  url          = {https://rlhfbook.com},
}
```
