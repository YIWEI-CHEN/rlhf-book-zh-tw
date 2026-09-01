#!/usr/bin/env python3
"""RLHF 中文版建置腳本：
1. 合併 content/ch06a.md + ch06b.md → ch06.md
2. 從 PDF 抽出並正規化參考文獻 → content/bibliography.md
3. 將各章 [N] 引用轉成可點擊的文獻連結
4. 將 content/*.md 包裝成 webapp/chapters/*.html
5. 產生 webapp/index.html 目錄頁
重新執行即可整站重建。
"""
import html
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
WEBAPP = os.path.join(ROOT, "webapp")
CHAPDIR = os.path.join(WEBAPP, "chapters")
PDF = os.path.join(ROOT, "RL_from_human_feedback.pdf")
BIBLIOGRAPHY = os.path.join(CONTENT, "bibliography.md")
BIBLIOGRAPHY_DATA = os.path.join(WEBAPP, "assets", "bibliography.json")

BIBLIOGRAPHY_HEADER = [
    "# 參考文獻（Bibliography）",
    "",
    "> 依原書保留原文，不另翻譯。編號對應各章引用標記 [N]。",
    "",
]

# Citation-looking tokens inside code and mathematics are not references.
PROTECTED_MARKDOWN = re.compile(
    r"(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`|\$\$[\s\S]*?\$\$|\$(?:\\.|[^$\n\\])+?\$)"
)

CHAPTERS = [
    dict(id="ch01", no="第 1 章", zh="導論", en="Introduction",
         desc="RLHF 是什麼、為何誕生、三步驟流程與後訓練的整體直覺。"),
    dict(id="ch02", no="第 2 章", zh="RLHF 簡史", en="A Tiny History of RLHF",
         desc="從偏好式 RL 的起源、語言模型時代，到 ChatGPT 之後的爆發。"),
    dict(id="ch03", no="第 3 章", zh="訓練總覽", en="Training Overview",
         desc="問題形式化、RL 設定的調整，與 InstructGPT／Tülu 3／DeepSeek R1 的經典配方。"),
    dict(id="ch04", no="第 4 章", zh="指令微調", en="Instruction Fine-Tuning",
         desc="聊天模板、指令資料的最佳實務與實作細節。"),
    dict(id="ch05", no="第 5 章", zh="獎勵模型", en="Reward Modeling",
         desc="Bradley-Terry 模型、架構與實作、ORM／PRM 與 LLM-as-a-judge。"),
    dict(id="ch06", no="第 6 章", zh="強化學習", en="Reinforcement Learning",
         desc="策略梯度推導、REINFORCE／PPO／GRPO 全家族與實作要點。"),
    dict(id="ch07", no="第 7 章", zh="推理與推論時擴展", en="Reasoning & Inference-Time Scaling",
         desc="RLVR 的角色、推理模型的起源與訓練慣例。"),
    dict(id="ch08", no="第 8 章", zh="直接對齊演算法", en="Direct-Alignment Algorithms",
         desc="DPO 的原理與完整推導、數值疑慮與線上／離線之辨。"),
    dict(id="ch09", no="第 9 章", zh="拒絕採樣", en="Rejection Sampling",
         desc="生成、評分、微調的逐步流程與 Best-of-N 採樣。"),
    dict(id="ch10", no="第 10 章", zh="偏好的本質", en="The Nature of Preferences",
         desc="從經濟學、哲學到最適控制：偏好與效用的跨領域根源。"),
    dict(id="ch11", no="第 11 章", zh="偏好資料", en="Preference Data",
         desc="標註介面、排序與評分、資料來源與偏誤陷阱。"),
    dict(id="ch12", no="第 12 章", zh="合成資料與蒸餾", en="Synthetic Data & Distillation",
         desc="蒸餾、on-policy 師生訓練、AI 回饋與憲法式 AI。"),
    dict(id="ch13", no="第 13 章", zh="工具使用與函式呼叫", en="Tool Use & Function Calling",
         desc="工具呼叫的生成交織、多步驟推理與 MCP。"),
    dict(id="ch14", no="第 14 章", zh="過度最佳化", en="Over-Optimization",
         desc="Goodhart 定律、代理目標的質性與量化失控。"),
    dict(id="ch15", no="第 15 章", zh="正則化", en="Regularization",
         desc="KL 懲罰、隱性正則化，與「SFT 記憶、RL 泛化」。"),
    dict(id="ch16", no="第 16 章", zh="評估", en="Evaluation",
         desc="提示格式、外部評比為何不可靠、污染與工具鏈。"),
    dict(id="ch17", no="第 17 章", zh="打造模型性格與產品", en="Model Character & Products",
         desc="性格訓練、persona 向量、模型規格與產品週期。"),
    dict(id="appa", no="附錄 A", zh="定義", en="Definitions",
         desc="全書使用的符號、定義與延伸詞彙表。"),
    dict(id="appb", no="附錄 B", zh="不只是「風格」", en='Beyond "Just Style"',
         desc="為何風格是溝通的載體，以及話多的平衡。"),
    dict(id="appc", no="附錄 C", zh="實務議題", en="Practical Issues",
         desc="後訓練的運算成本、評估變異與異常任務辨識。"),
    dict(id="bibliography", no="參考文獻", zh="參考文獻", en="Bibliography",
         desc="全書引用文獻（保留原文）。"),
]

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — RLHF 中文版</title>
<link rel="stylesheet" href="../assets/katex/katex.min.css">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="../index.html">RLHF 中文版<span>從人類回饋中強化學習</span></a>
  <nav class="chapnav">{prev_top}<span class="chapnav-current">{no}</span>{next_top}<a class="gh-star" href="https://github.com/ai-twinkle/rlhf-book-zh-tw" target="_blank" rel="noopener" data-gh-repo="ai-twinkle/rlhf-book-zh-tw"><span class="star-ico">★</span><span class="gh-label">Star</span><b class="gh-count" hidden></b></a></nav>
</header>
<div class="layout">
  <aside class="sidebar"><nav id="toc" class="toc"><h2>本章目錄</h2></nav></aside>
  <main class="main">
    <div id="lab-banner"></div>
    <article id="content" class="prose"></article>
    <section id="lab" class="lab" hidden>
      <h2 class="lab-title">🧪 互動實驗室</h2>
      <div id="lab-intro"></div>
      <div id="lab-root"></div>
    </section>
    <nav class="pager">{prev_card}{next_card}</nav>
    <footer class="pagefoot">本站為 <a href="https://github.com/ai-twinkle">Twinkle AI Community</a>（台灣）的<strong>非官方社群翻譯</strong>（unofficial community translation）· 譯自 Nathan Lambert,《Reinforcement Learning from Human Feedback》（<a href="https://rlhfbook.com">rlhfbook.com</a>）· 依 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant">CC BY-NC-SA 4.0</a> 授權，僅供學習研究、不得作商業用途。</footer>
  </main>
</div>
<script type="text/markdown" id="chapter-md">
{md}
</script>
<script src="../assets/marked.min.js"></script>
<script src="../assets/katex/katex.min.js"></script>
<script src="../assets/katex/auto-render.min.js"></script>
{widget_tag}<script src="../assets/app.js"></script>
<script src="../assets/gh-star.js"></script>
</body>
</html>
"""

INDEX_TMPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RLHF 中文版 — 從人類回饋中強化學習</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<section class="hero">
  <div class="eyebrow">繁體中文全譯本 · 互動版</div>
  <h1>從人類回饋中強化學習<br>Reinforcement Learning from Human Feedback</h1>
  <p class="sub">Nathan Lambert 著。一本聚焦語言模型的 RLHF 與後訓練（post-training）簡明導論：從指令微調、獎勵模型，到 PPO／GRPO、DPO、拒絕採樣與推理模型。每一章都附有互動實驗，邊玩邊懂核心概念。</p>
  <p class="sub" style="font-size:.82rem">由台灣 <a href="https://github.com/ai-twinkle">Twinkle AI Community</a> 翻譯維護的非官方社群翻譯版本。</p>
  <div class="meta">
    <div><b>{n_ch}</b>章節</div>
    <div><b>{n_app}</b>附錄</div>
    <div><b>{n_fig}</b>插圖</div>
    <div><b>{n_lab}</b>互動實驗</div>
    <a href="https://github.com/ai-twinkle/rlhf-book-zh-tw" target="_blank" rel="noopener" data-gh-repo="ai-twinkle/rlhf-book-zh-tw"><b class="gh-count">—</b>GitHub ★</a>
  </div>
</section>
<div class="grid-wrap">
  <h2>章節</h2>
  <div class="chapter-grid">
{chapter_cards}
  </div>
  <h2>附錄與文獻</h2>
  <div class="chapter-grid">
{appendix_cards}
  </div>
</div>
<footer class="foot">本站為 <a href="https://github.com/ai-twinkle">Twinkle AI Community</a>（台灣）的<strong>非官方社群翻譯</strong>（unofficial community translation），已獲原作者知悉（<a href="https://github.com/natolambert/rlhf-book/issues/472">rlhf-book#472</a>）· 譯自 Nathan Lambert,《Reinforcement Learning from Human Feedback》（<a href="https://rlhfbook.com">rlhfbook.com</a>，2026-07-01 版）· 依 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant">CC BY-NC-SA 4.0</a> 授權翻譯，僅供學習研究、不得作商業用途 · 支持原作者請購買<a href="https://rlhfbook.com">實體書</a> · <a href="https://github.com/ai-twinkle/rlhf-book-zh-tw">GitHub 原始碼</a></footer>
<script src="assets/gh-star.js"></script>
</body>
</html>
"""


def merge_ch06():
    a, b = os.path.join(CONTENT, "ch06a.md"), os.path.join(CONTENT, "ch06b.md")
    if os.path.exists(a) and os.path.exists(b):
        with open(a, encoding="utf-8") as f1, open(b, encoding="utf-8") as f2:
            merged = f1.read().rstrip() + "\n\n" + f2.read().lstrip()
        with open(os.path.join(CONTENT, "ch06.md"), "w", encoding="utf-8") as f:
            f.write(merged)
        print("merged ch06a + ch06b -> ch06.md")


def parse_bibliography(raw):
    """Recover numbered references, including entries merged at PDF page breaks."""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    raw = raw.replace("\f", "\n")

    # pdftotext inserts a footer between the previous entry and the next [N].
    raw = re.sub(r"rlhfbook\.com\s+\d+\s*", " ", raw)
    raw = re.sub(r"\[(\d+)\]\s+", r"\n\1. ", raw)

    # Repair URLs that were split between the scheme and // in the PDF.
    raw = re.sub(
        r"\b(https?)\s*:\s*//\s*",
        lambda m: m.group(1).lower() + "://",
        raw,
        flags=re.IGNORECASE,
    )

    markers = list(re.finditer(r"(?m)^(\d+)\.\s+", raw))
    entries = []
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(raw)
        number = int(marker.group(1))
        text = re.sub(r"\s+", " ", raw[marker.end():end]).strip()
        entries.append((number, text))

    numbers = [number for number, _ in entries]
    expected = list(range(1, numbers[-1] + 1)) if numbers else []
    if numbers != expected:
        missing = sorted(set(expected) - set(numbers))
        duplicates = sorted({number for number in numbers if numbers.count(number) > 1})
        raise ValueError(
            "bibliography numbering is not contiguous; "
            f"missing={missing}, duplicates={duplicates}"
        )
    return entries


def format_bibliography(entries):
    lines = BIBLIOGRAPHY_HEADER.copy()
    lines.extend(f"{number}. {text}" for number, text in entries)
    return "\n".join(lines) + "\n"


def extract_bibliography():
    if os.path.exists(BIBLIOGRAPHY):
        return
    txt = subprocess.run(
        ["pdftotext", "-raw", "-f", "205", "-l", "226", PDF, "-"],
        capture_output=True, text=True, check=True).stdout
    txt = re.sub(r"-\n(?=[a-z])", "", txt)  # repair split words
    entries = parse_bibliography(txt)
    with open(BIBLIOGRAPHY, "w", encoding="utf-8") as f:
        f.write(format_bibliography(entries))
    print(f"extracted bibliography ({len(entries)} entries)")


def normalize_bibliography():
    """Make an existing PDF-derived bibliography complete and idempotent."""
    with open(BIBLIOGRAPHY, encoding="utf-8") as f:
        current = f.read()
    entries = parse_bibliography(current)
    normalized = format_bibliography(entries)
    if current != normalized:
        with open(BIBLIOGRAPHY, "w", encoding="utf-8") as f:
            f.write(normalized)
        print(f"normalized bibliography ({len(entries)} entries)")
    return entries


def build_bibliography_data(entries):
    """Write the shared reference lookup used by citation hover tooltips."""
    payload = {str(number): text for number, text in entries}
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    current = ""
    if os.path.exists(BIBLIOGRAPHY_DATA):
        with open(BIBLIOGRAPHY_DATA, encoding="utf-8") as f:
            current = f.read()
    if current != serialized:
        with open(BIBLIOGRAPHY_DATA, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"built bibliography tooltip data ({len(entries)} entries)")


def link_citations(md, valid_references):
    """Link prose citations across every chapter while protecting code and math."""
    missing = set()

    def replace_unprotected(segment):
        def replace(match):
            number = int(match.group(1))
            if number not in valid_references:
                missing.add(number)
                return match.group(0)
            return f"[[{number}]](bibliography.html#ref-{number})"

        return re.sub(r"(?<!!)\[([1-9]\d*)\](?!\s*\()", replace, segment)

    segments = PROTECTED_MARKDOWN.split(md)
    linked = "".join(
        segment if i % 2 else replace_unprotected(segment)
        for i, segment in enumerate(segments)
    )
    if missing:
        raise ValueError(f"citations missing from bibliography: {sorted(missing)}")
    return linked


def build_pages():
    os.makedirs(CHAPDIR, exist_ok=True)
    bibliography_entries = normalize_bibliography()
    build_bibliography_data(bibliography_entries)
    valid_references = {number for number, _ in bibliography_entries}
    built = {}
    for ch in CHAPTERS:
        src = os.path.join(CONTENT, ch["id"] + ".md")
        built[ch["id"]] = os.path.exists(src)
    n_built = 0
    for i, ch in enumerate(CHAPTERS):
        src = os.path.join(CONTENT, ch["id"] + ".md")
        if not built[ch["id"]]:
            continue
        with open(src, encoding="utf-8") as f:
            md = f.read().replace("</script", "<\\/script")
        if ch["id"] != "bibliography":
            md = link_citations(md, valid_references)
        prev = next((c for c in reversed(CHAPTERS[:i]) if built[c["id"]]), None)
        nxt = next((c for c in CHAPTERS[i + 1:] if built[c["id"]]), None)
        prev_top = f'<a href="{prev["id"]}.html">← {prev["no"]}</a>' if prev else ""
        next_top = f'<a href="{nxt["id"]}.html">{nxt["no"]} →</a>' if nxt else ""
        prev_card = (f'<a class="prev" href="{prev["id"]}.html"><span class="dir">← 上一章</span>'
                     f'<div class="ttl">{prev["no"]}　{prev["zh"]}</div></a>') if prev else "<span></span>"
        next_card = (f'<a class="next" href="{nxt["id"]}.html"><span class="dir">下一章 →</span>'
                     f'<div class="ttl">{nxt["no"]}　{nxt["zh"]}</div></a>') if nxt else ""
        widget = os.path.join(WEBAPP, "assets", "widgets", ch["id"] + ".js")
        widget_tag = (f'<script src="../assets/widgets/{ch["id"]}.js"></script>\n'
                      if os.path.exists(widget) else "")
        page = PAGE_TMPL.format(
            title=f'{ch["no"]}　{ch["zh"]}', no=f'{ch["no"]}　{ch["zh"]}',
            prev_top=prev_top, next_top=next_top,
            prev_card=prev_card, next_card=next_card,
            md=md, widget_tag=widget_tag)
        with open(os.path.join(CHAPDIR, ch["id"] + ".html"), "w", encoding="utf-8") as f:
            f.write(page)
        n_built += 1
    return built, n_built


def build_index(built):
    def card(ch):
        has_widget = os.path.exists(os.path.join(WEBAPP, "assets", "widgets", ch["id"] + ".js"))
        badge = '<span class="badge">互動實驗</span>' if has_widget else ""
        inner = (f'{badge}<span class="no">{html.escape(ch["no"])}</span>'
                 f'<span class="zh">{html.escape(ch["zh"])}</span>'
                 f'<span class="en">{html.escape(ch["en"])}</span>'
                 f'<span class="desc">{html.escape(ch["desc"])}</span>')
        if built.get(ch["id"]):
            return f'    <a class="card" href="chapters/{ch["id"]}.html">{inner}</a>'
        return f'    <div class="card disabled">{inner}<span class="badge">翻譯中</span></div>'

    ch_cards = "\n".join(card(c) for c in CHAPTERS if c["id"].startswith("ch"))
    app_cards = "\n".join(card(c) for c in CHAPTERS if not c["id"].startswith("ch"))
    figdir = os.path.join(WEBAPP, "assets", "figures")
    n_fig = len([f for f in os.listdir(figdir) if f.endswith(".png")]) if os.path.isdir(figdir) else 0
    widgets = os.path.join(WEBAPP, "assets", "widgets")
    n_lab = len([f for f in os.listdir(widgets) if f.endswith(".js")]) if os.path.isdir(widgets) else 0
    page = INDEX_TMPL.format(n_ch=17, n_app=3, n_fig=n_fig, n_lab=n_lab,
                             chapter_cards=ch_cards, appendix_cards=app_cards)
    with open(os.path.join(WEBAPP, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


if __name__ == "__main__":
    merge_ch06()
    extract_bibliography()
    built, n = build_pages()
    build_index(built)
    missing = [k for k, v in built.items() if not v]
    print(f"built {n} chapter pages; missing: {', '.join(missing) if missing else 'none'}")
