/* RLHF 中文版 — 章節頁渲染器：markdown → HTML、KaTeX 數學、側欄目錄、互動元件掛載 */
(function () {
  const mdEl = document.getElementById('chapter-md');
  const content = document.getElementById('content');
  if (!mdEl || !content) return;

  let md = mdEl.textContent
    .replaceAll('<\\/script', '</script')
    .replaceAll('../webapp/assets/', '../assets/');

  // 先把數學片段抽出，避免 marked 把 LaTeX 的 _ * 當成 markdown 語法
  const mathStore = [];
  const stash = (s) => { mathStore.push(s); return '⦀M' + (mathStore.length - 1) + '⦀'; };
  // 跳過程式碼區塊，僅在一般文字中抽取數學
  const segments = md.split(/(```[\s\S]*?```|`[^`\n]*`)/g);
  md = segments.map((seg, i) => {
    if (i % 2 === 1) return seg; // code 片段原樣保留
    return seg
      .replace(/\$\$([\s\S]+?)\$\$/g, (m) => stash(m))
      .replace(/\$(?!\s)((?:\\.|[^$\n\\])+?)(?<!\s)\$/g, (m) => stash(m));
  }).join('');

  let html = marked.parse(md, { mangle: false });
  html = html.replace(/⦀M(\d+)⦀/g, (_, i) => mathStore[+i]
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'));
  content.innerHTML = html;

  if (window.renderMathInElement) {
    renderMathInElement(content, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
      ],
      throwOnError: false,
    });
  }

  // 全書共用 citation 導覽：章節的 [N] 連到文獻，文獻條目提供穩定錨點。
  const pageName = window.location.pathname.split('/').pop();
  if (pageName === 'bibliography.html') {
    const bibliography = [...content.children].find((el) => el.tagName === 'OL');
    if (bibliography) {
      bibliography.classList.add('bibliography-list');
      bibliography.querySelectorAll(':scope > li').forEach((entry, i) => {
        const number = i + 1;
        entry.id = 'ref-' + number;
        entry.value = number;
      });
    }
    if (/^#ref-\d+$/.test(window.location.hash)) {
      requestAnimationFrame(() => {
        const target = document.getElementById(window.location.hash.slice(1));
        if (target) target.scrollIntoView({ block: 'center' });
      });
    }
  } else {
    const citations = [...content.querySelectorAll('a[href^="bibliography.html#ref-"]')];
    citations.forEach((citation) => {
      citation.classList.add('citation');
      citation.setAttribute('aria-label', '查看參考文獻 ' + citation.textContent);
    });

    if (citations.length) {
      const tooltip = document.createElement('div');
      tooltip.id = 'citation-tooltip';
      tooltip.className = 'citation-tooltip';
      tooltip.setAttribute('role', 'tooltip');
      tooltip.hidden = true;

      const tooltipText = document.createElement('span');
      tooltipText.className = 'citation-tooltip-text';
      tooltip.appendChild(tooltipText);
      document.body.appendChild(tooltip);

      let activeCitation = null;
      let hideTimer = null;
      let bibliographyPromise = null;

      const loadBibliography = () => {
        if (!bibliographyPromise) {
          bibliographyPromise = fetch('../assets/bibliography.json')
            .then((response) => {
              if (!response.ok) throw new Error('HTTP ' + response.status);
              return response.json();
            });
        }
        return bibliographyPromise;
      };

      const positionTooltip = (citation) => {
        if (!citation || tooltip.hidden) return;
        tooltip.style.visibility = 'hidden';
        tooltip.style.left = '0px';
        tooltip.style.top = '0px';

        const anchorRect = citation.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const edge = 10;
        const gap = 10;
        let left = anchorRect.left + anchorRect.width / 2 - tooltipRect.width / 2;
        left = Math.max(edge, Math.min(left, window.innerWidth - tooltipRect.width - edge));
        let top = anchorRect.top - tooltipRect.height - gap;
        if (top < edge) top = anchorRect.bottom + gap;

        tooltip.style.left = left + 'px';
        tooltip.style.top = top + 'px';
        tooltip.style.visibility = 'visible';
      };

      const hideTooltip = () => {
        if (activeCitation) activeCitation.removeAttribute('aria-describedby');
        activeCitation = null;
        tooltip.hidden = true;
      };

      const scheduleHide = () => {
        window.clearTimeout(hideTimer);
        hideTimer = window.setTimeout(hideTooltip, 120);
      };

      const showTooltip = async (citation) => {
        window.clearTimeout(hideTimer);
        const match = citation.getAttribute('href').match(/#ref-(\d+)$/);
        if (!match) return;
        const number = match[1];

        if (activeCitation && activeCitation !== citation) {
          activeCitation.removeAttribute('aria-describedby');
        }
        activeCitation = citation;
        citation.setAttribute('aria-describedby', tooltip.id);
        tooltipText.textContent = '載入中…';
        tooltip.hidden = false;
        positionTooltip(citation);

        try {
          const bibliography = await loadBibliography();
          if (activeCitation !== citation) return;
          tooltipText.textContent = bibliography[number] || '找不到這筆參考文獻。';
        } catch (error) {
          if (activeCitation !== citation) return;
          tooltipText.textContent = '無法載入參考文獻內容。';
          console.error('bibliography tooltip failed:', error);
        }
        positionTooltip(citation);
      };

      citations.forEach((citation) => {
        citation.addEventListener('mouseenter', () => showTooltip(citation));
        citation.addEventListener('mouseleave', scheduleHide);
        citation.addEventListener('focus', () => showTooltip(citation));
        citation.addEventListener('blur', scheduleHide);
      });
      window.addEventListener('resize', () => positionTooltip(activeCitation));
      window.addEventListener('scroll', () => positionTooltip(activeCitation), { passive: true });
      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') hideTooltip();
      });
    }
  }

  // 側欄目錄（h2 / h3）＋捲動高亮
  const toc = document.getElementById('toc');
  const heads = content.querySelectorAll('h2, h3');
  if (toc && heads.length) {
    const ol = document.createElement('ol');
    heads.forEach((h, i) => {
      h.id = 'sec-' + i;
      const li = document.createElement('li');
      li.className = 'toc-' + h.tagName.toLowerCase();
      const a = document.createElement('a');
      a.href = '#sec-' + i;
      a.textContent = h.textContent.replace(/（[^）]*）$/, '');
      li.appendChild(a);
      ol.appendChild(li);
    });
    toc.appendChild(ol);
    const links = toc.querySelectorAll('a');
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const idx = [...heads].indexOf(e.target);
        links.forEach((l, i) => l.classList.toggle('active', i === idx));
      });
    }, { rootMargin: '-10% 0px -75% 0px' });
    heads.forEach((h) => spy.observe(h));
  }

  // 互動元件掛載
  const lab = document.getElementById('lab');
  const w = window.ChapterWidget;
  if (lab && w && typeof w.render === 'function') {
    lab.hidden = false;
    if (w.title) lab.querySelector('.lab-title').textContent = '🧪 互動實驗室 · ' + w.title;
    if (w.intro) {
      const introEl = document.getElementById('lab-intro');
      introEl.className = 'lab-intro';
      introEl.textContent = w.intro;
    }
    // 內文頂部放一張前往實驗室的提示卡
    const banner = document.getElementById('lab-banner');
    if (banner) {
      banner.className = 'lab-banner';
      banner.innerHTML = '🧪 本章附有互動實驗：<a href="#lab">' + (w.title || '前往實驗室') + ' ↓</a>';
    }
    try {
      w.render(document.getElementById('lab-root'));
    } catch (err) {
      console.error('widget render failed:', err);
      lab.hidden = true;
    }
  }
})();
