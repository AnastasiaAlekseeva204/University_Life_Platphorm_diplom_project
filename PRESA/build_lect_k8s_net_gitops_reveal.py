# -*- coding: utf-8 -*-
"""lect_k8s.md -> lect_k8s.html (Reveal.js, стиль по мотивам lect-arch-mq.html).

В блоке ```mermaid первая строка @large (отдельной строкой) даёт класс mermaid-wrap--large — крупнее шрифт на проекторе.
Блок ```k8s-cluster-diagram вставляет HTML-схему слайда 12 (читаемые подписи без Mermaid).
"""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD = HERE / "lect_k8s.md"
OUT = HERE / "lect_k8s.html"
REVEAL_BASE = "../../../SEMESTR-1/15-16"

TRANSITIONS = ("slide", "fade", "convex", "zoom", "slide")
BG_COLORS = ("#0d1117", "#111827", "#0f172a", "#1e1b4b", "#0c4a6e", "#134e4a")

# Слайд 12: HTML вместо Mermaid — подписи не обрезаются в Reveal.
K8S_SLIDE12_CLUSTER_DIAGRAM = """
<div class="k8s-cluster-diagram" role="img" aria-label="Схема: Control Plane и рабочие ноды Kubernetes">
  <div class="k8s-cluster-grid">
    <div class="k8s-cluster-cp k8s-cluster-panel">
      <div class="k8s-cluster-panel-title">Пульт: Control Plane</div>
      <div class="k8s-cluster-vstack">
        <div class="k8s-cluster-block">Планировщик + контроллеры<br><span class="k8s-cluster-sub">scheduler, controller-manager</span></div>
        <div class="k8s-cluster-arr">↓</div>
        <div class="k8s-cluster-block">kubectl / CI</div>
        <div class="k8s-cluster-arr">↓</div>
        <div class="k8s-cluster-block k8s-cluster-block-accent">API Server<br><span class="k8s-cluster-sub">kube-apiserver</span></div>
        <div class="k8s-cluster-hrow">
          <span class="k8s-cluster-arrh">↔</span>
          <div class="k8s-cluster-block k8s-cluster-etcd">etcd<br><span class="k8s-cluster-sub">память кластера</span></div>
        </div>
      </div>
    </div>
    <div class="k8s-cluster-bridge">
      <div class="k8s-cluster-bridge-row">
        <span class="k8s-cluster-bridge-arrows">⇄</span>
        <div class="k8s-cluster-bridge-cap">watch,<br>команды</div>
      </div>
      <div class="k8s-cluster-bridge-row">
        <span class="k8s-cluster-bridge-arrows">⇄</span>
        <div class="k8s-cluster-bridge-cap">watch,<br>команды</div>
      </div>
    </div>
    <div class="k8s-cluster-workers">
      <div class="k8s-cluster-panel k8s-cluster-worker">
        <div class="k8s-cluster-panel-title">Рабочая нода</div>
        <div class="k8s-cluster-vstack">
          <div class="k8s-cluster-block">kubelet</div>
          <div class="k8s-cluster-arr">↓</div>
          <div class="k8s-cluster-block">движок контейнеров</div>
          <div class="k8s-cluster-arr">↓</div>
          <div class="k8s-cluster-block">ваши Pod</div>
        </div>
      </div>
      <div class="k8s-cluster-panel k8s-cluster-worker">
        <div class="k8s-cluster-panel-title">Рабочая нода …</div>
        <div class="k8s-cluster-vstack">
          <div class="k8s-cluster-block">kubelet</div>
          <div class="k8s-cluster-arr">↓</div>
          <div class="k8s-cluster-block">Pod …</div>
        </div>
      </div>
    </div>
  </div>
</div>
""".strip()


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def inline_md(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r'<code class="k8s-code">\1</code>', s)
    return s


def esc_mermaid(s: str) -> str:
    return html.escape(s, quote=False)


def slide_body_to_html(body: str) -> str:
    lines = body.strip().split("\n")
    out: list[str] = []
    i = 0
    list_tag: str | None = None  # "ul" or "ol"

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            close_list()
            i += 1
            continue

        if stripped.startswith("```"):
            close_list()
            lang = stripped[3:].strip() or "text"
            chunk: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                chunk.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code = "\n".join(chunk)
            if lang == "mermaid":
                code_st = code.strip()
                lines_m = code_st.split("\n")
                wrap_extra = ""
                if lines_m and lines_m[0].strip() == "@large":
                    lines_m = lines_m[1:]
                    wrap_extra = " mermaid-wrap--large"
                    code_st = "\n".join(lines_m)
                out.append(
                    f'<div class="mermaid-wrap{wrap_extra} fragment"><div class="mermaid">{esc_mermaid(code_st)}</div></div>'
                )
            elif lang == "k8s-cluster-diagram":
                out.append(f'<div class="k8s-cluster-wrap fragment">{K8S_SLIDE12_CLUSTER_DIAGRAM}</div>')
            else:
                hl = "yaml" if lang == "yaml" else ("plaintext" if lang == "text" else lang)
                out.append(
                    f'<pre class="k8s-pre fragment"><code class="hljs language-{hl}">{esc(code)}</code></pre>'
                )
            continue

        if "|" in stripped and stripped.startswith("|"):
            close_list()
            rows: list[str] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                row = lines[i].strip()
                cells = [c.strip() for c in row.split("|")[1:-1]]
                if all(re.match(r"^[\s\-:]+$", re.sub(r"\s", "", c)) for c in cells if c):
                    i += 1
                    continue
                rows.append(cells)
                i += 1
            if rows:
                out.append('<table class="k8s-table fragment">')
                for ri, row in enumerate(rows):
                    tag = "th" if ri == 0 else "td"
                    out.append("<tr>")
                    for c in row:
                        out.append(f"<{tag}>{inline_md(c)}</{tag}>")
                    out.append("</tr>")
                out.append("</table>")
            continue

        if stripped.startswith(">"):
            close_list()
            qlines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                qlines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append('<div class="k8s-quote fragment">' + "<br>".join(inline_md(x) for x in qlines) + "</div>")
            continue

        if stripped.startswith("* ") or stripped.startswith("- "):
            if list_tag != "ul":
                close_list()
                out.append('<ul class="k8s-ul">')
                list_tag = "ul"
            text = stripped[2:].strip()
            out.append(f'<li class="fragment fade-in-then-semi-out">{inline_md(text)}</li>')
            i += 1
            continue

        if re.match(r"^\d+\.\s", stripped):
            if list_tag != "ol":
                close_list()
                out.append('<ol class="k8s-ol">')
                list_tag = "ol"
            text = re.sub(r"^\d+\.\s", "", stripped)
            out.append(f'<li class="fragment">{inline_md(text)}</li>')
            i += 1
            continue

        close_list()
        if stripped.startswith("**") and stripped.endswith("**") and stripped.count("**") == 2:
            inner = stripped[2:-2]
            out.append(f'<p class="fragment"><strong class="k8s-lead">{esc(inner)}</strong></p>')
        else:
            out.append(f'<p class="fragment">{inline_md(stripped)}</p>')
        i += 1

    close_list()
    return "\n".join(out)


def split_slides(md: str) -> list[tuple[str, str]]:
    md = re.split(r"\n## Примечание для оформления", md, maxsplit=1)[0]
    parts = re.split(r"(?m)^(# Слайд \d+[a-z]?\.\s*.+)$", md)
    slides: list[tuple[str, str]] = []
    if not parts:
        return slides
    i = 0
    while i < len(parts):
        if re.match(r"^# Слайд \d+[a-z]?\.", parts[i].strip()):
            title_line = parts[i].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            slides.append((title_line, body))
            i += 2
        else:
            i += 1
    return slides


def main():
    raw = MD.read_text(encoding="utf-8")
    slides = split_slides(raw)
    sections: list[str] = []

    for idx, (title_line, body) in enumerate(slides):
        m = re.match(r"^# (Слайд \d+[a-z]?)\.\s*(.+)$", title_line.strip())
        if not m:
            continue
        num, title = m.group(1), m.group(2).strip()
        h2 = f"{num}. {title}"
        trans = TRANSITIONS[idx % len(TRANSITIONS)]
        bg = BG_COLORS[idx % len(BG_COLORS)]
        body_lines = body.rstrip().split("\n")
        while body_lines and body_lines[-1].strip() == "---":
            body_lines.pop()
        inner = slide_body_to_html("\n".join(body_lines))
        sections.append(
            f"""<section data-transition="{trans}" data-background-color="{bg}" class="k8s-slide">
  <h2>{esc(h2)}</h2>
  <div class="k8s-slide-inner">
{inner}
  </div>
</section>"""
        )

    title_slide = f"""<section data-transition="zoom" data-background-gradient="linear-gradient(135deg,#0d1117 0%,#1e3a5f 40%,#326CE5 100%)" class="k8s-title-slide">
  <div class="k8s-title-card">
    <div class="k8s-helm">☸</div>
    <h1 class="k8s-title-h1">Kubernetes</h1>
    <p class="k8s-title-sub">Зачем и как он работает — на пальцах</p>
    <p class="k8s-title-meta fragment">Лекция · {len(sections)} слайдов · оркестрация контейнеров</p>
  </div>
</section>"""

    sections_html = "\n\n".join([title_slide] + sections)

    html_doc = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kubernetes: зачем и как он работает</title>
  <link rel="stylesheet" href="{REVEAL_BASE}/css/reveal.min.css">
  <link rel="stylesheet" href="{REVEAL_BASE}/css/black.min.css">
  <link rel="stylesheet" href="{REVEAL_BASE}/css/monokai.min.css">
  <style>
    @keyframes k8s-glow {{
      0%, 100% {{ text-shadow: 0 0 20px rgba(50,108,229,0.5), 0 0 40px rgba(50,108,229,0.2); }}
      50% {{ text-shadow: 0 0 30px rgba(50,108,229,0.8), 0 0 60px rgba(0,212,170,0.25); }}
    }}
    @keyframes k8s-float {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-6px); }}
    }}
    html, body, .reveal-viewport, .reveal, .reveal .slides, .reveal .slide-background-content {{
      overflow: hidden !important;
      scrollbar-width: none !important;
    }}
    /* Reveal по умолчанию центрирует .slides через translate(-50%, -50%); не убирать Y — иначе контент «падает» вниз */
    .reveal .slides section.k8s-slide {{
      overflow-y: auto !important;
      justify-content: center !important;
      padding-top: 12px !important;
      padding-bottom: 12px !important;
    }}
    .reveal .slides {{
      width: 82% !important;
      height: 92% !important;
      left: 50% !important;
      top: 50% !important;
      transform: translate(-50%, -50%) scale(1.12) !important;
      transform-origin: center center !important;
    }}
    .reveal .slides section {{
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
      justify-content: center !important;
      padding: 20px 28px !important;
      font-size: 0.88em !important;
      max-width: 100% !important;
      text-align: center !important;
      line-height: 1.48 !important;
    }}
    .reveal h1 {{
      font-size: 1.85em !important;
      color: #fff !important;
      animation: k8s-glow 4s ease-in-out infinite !important;
    }}
    .reveal h2 {{
      font-size: 1.05em !important;
      color: #7eb8ff !important;
      border-bottom: 2px solid rgba(50,108,229,0.55) !important;
      padding-bottom: 0.35em !important;
      margin-bottom: 0.45em !important;
      width: 100% !important;
      text-transform: none !important;
    }}
    .k8s-title-slide .k8s-title-h1 {{
      font-size: 2.2em !important;
      background: linear-gradient(90deg, #fff, #7eb8ff, #00d4aa);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent !important;
      animation: k8s-glow 3s ease-in-out infinite !important;
    }}
    .k8s-title-card {{
      background: rgba(13,17,23,0.75);
      border: 2px solid rgba(50,108,229,0.6);
      border-radius: 16px;
      padding: 36px 48px;
      max-width: 92%;
      box-shadow: 0 12px 48px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
    }}
    .k8s-helm {{
      font-size: 3.5rem;
      line-height: 1;
      margin-bottom: 0.2em;
      animation: k8s-float 3.5s ease-in-out infinite;
      filter: drop-shadow(0 0 12px rgba(50,108,229,0.7));
    }}
    .k8s-title-sub {{
      font-size: 1.15em !important;
      color: #c9d1d9 !important;
      margin-top: 0.5em !important;
    }}
    .k8s-title-meta {{
      color: #8b949e !important;
      font-size: 0.9em !important;
      margin-top: 1em !important;
    }}
    .k8s-slide-inner {{
      width: 100%;
      max-width: 100%;
      text-align: left;
    }}
    .k8s-slide-inner p {{
      margin: 0.35em 0;
      text-align: left;
    }}
    .k8s-ul, .k8s-ol {{
      margin: 0.4em auto !important;
      max-width: 95%;
      text-align: left !important;
    }}
    .k8s-ul li {{
      margin-bottom: 0.45em !important;
      list-style: none !important;
      position: relative !important;
      padding-left: 1.1em !important;
    }}
    .k8s-ul li::before {{
      content: "▸";
      position: absolute;
      left: 0;
      color: #326CE5;
      font-weight: bold;
    }}
    .k8s-ol {{
      list-style: decimal !important;
      padding-left: 1.6em !important;
      margin-left: 0.5em !important;
    }}
    .k8s-ol li {{
      margin-bottom: 0.45em !important;
      padding-left: 0.15em !important;
    }}
    .k8s-code {{
      color: #79c0ff !important;
      background: rgba(110,118,129,0.2) !important;
      padding: 0.12em 0.35em !important;
      border-radius: 4px !important;
      font-size: 0.92em !important;
    }}
    .k8s-pre {{
      max-width: 100% !important;
      margin: 10px auto !important;
      border-radius: 10px !important;
      border: 1px solid rgba(50,108,229,0.45) !important;
      box-shadow: 0 6px 24px rgba(0,0,0,0.35) !important;
      text-align: left !important;
      font-size: 0.62em !important;
    }}
    .k8s-pre code {{
      padding: 12px 14px !important;
      line-height: 1.35 !important;
      white-space: pre-wrap !important;
      word-break: break-word !important;
      max-height: 52vh;
      overflow-y: auto;
      display: block;
    }}
    .mermaid-wrap {{
      max-width: 100%;
      margin: 8px auto;
    }}
    .mermaid-wrap--large {{
      max-width: 100%;
      margin: 12px auto 4px;
    }}
    .mermaid {{
      background: rgba(22,27,34,0.9) !important;
      border-radius: 10px !important;
      padding: 12px !important;
      border: 1px solid rgba(0,212,170,0.35) !important;
      text-align: center !important;
      font-size: 0.55em !important;
    }}
    .mermaid-wrap--large .mermaid {{
      font-size: 0.92em !important;
      padding: 18px 14px !important;
      min-height: 280px;
    }}
    .mermaid-wrap--large .mermaid svg {{
      max-width: 100% !important;
      height: auto !important;
    }}
    .k8s-cluster-wrap {{
      max-width: 100%;
      margin: 10px auto 6px;
      overflow: visible !important;
    }}
    .k8s-cluster-diagram {{
      font-size: clamp(15px, 2.5vmin, 20px) !important;
      line-height: 1.35 !important;
      color: #e6edf3 !important;
      text-align: left !important;
    }}
    .k8s-cluster-grid {{
      display: grid;
      grid-template-columns: minmax(200px, 1.15fr) minmax(56px, 0.2fr) minmax(168px, 0.95fr);
      grid-template-rows: 1fr 1fr;
      gap: 10px 8px;
      align-items: stretch;
    }}
    .k8s-cluster-cp {{
      grid-column: 1;
      grid-row: 1 / span 2;
      align-self: center;
    }}
    .k8s-cluster-bridge {{
      grid-column: 2;
      grid-row: 1 / span 2;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      align-items: center;
      padding: 6px 0;
      min-width: 52px;
    }}
    .k8s-cluster-bridge-row {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      color: #7ee0c5;
    }}
    .k8s-cluster-bridge-arrows {{
      font-size: 1.35em;
      line-height: 1;
    }}
    .k8s-cluster-bridge-cap {{
      font-size: 0.72em !important;
      text-align: center;
      line-height: 1.25;
      max-width: 4.5em;
      color: #a8f5e0;
    }}
    .k8s-cluster-workers {{
      grid-column: 3;
      grid-row: 1 / span 2;
      display: flex;
      flex-direction: column;
      gap: 10px;
      justify-content: center;
    }}
    .k8s-cluster-panel {{
      background: rgba(22,27,34,0.95) !important;
      border: 2px solid rgba(0,212,170,0.45) !important;
      border-radius: 12px !important;
      padding: 12px 14px !important;
    }}
    .k8s-cluster-panel-title {{
      font-size: 0.78em !important;
      font-weight: 700 !important;
      color: #00d4aa !important;
      margin: 0 0 10px 0 !important;
      text-transform: none;
      letter-spacing: 0.02em;
    }}
    .k8s-cluster-vstack {{
      display: flex;
      flex-direction: column;
      align-items: stretch;
    }}
    .k8s-cluster-block {{
      background: rgba(50,108,229,0.28) !important;
      border: 1px solid rgba(50,108,229,0.55) !important;
      border-radius: 8px !important;
      padding: 10px 12px !important;
      text-align: center !important;
      word-break: break-word;
      hyphens: auto;
    }}
    .k8s-cluster-block-accent {{
      background: rgba(50,108,229,0.45) !important;
      border-color: rgba(126,184,255,0.65) !important;
      font-weight: 600;
    }}
    .k8s-cluster-etcd {{
      border-style: dashed !important;
      border-color: rgba(0,212,170,0.5) !important;
    }}
    .k8s-cluster-sub {{
      display: block;
      font-size: 0.82em !important;
      font-weight: 400 !important;
      color: #8b949e !important;
      margin-top: 4px;
    }}
    .k8s-cluster-arr {{
      text-align: center;
      color: #7eb8ff;
      font-size: 0.95em;
      line-height: 1;
      padding: 2px 0;
    }}
    .k8s-cluster-hrow {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
    }}
    .k8s-cluster-arrh {{
      color: #7eb8ff;
      font-size: 1.1em;
      flex-shrink: 0;
    }}
    .k8s-cluster-hrow .k8s-cluster-block {{
      flex: 1;
    }}
    .k8s-cluster-worker .k8s-cluster-vstack .k8s-cluster-block {{
      padding: 8px 10px !important;
    }}
    @media (max-width: 900px) {{
      .k8s-cluster-grid {{
        grid-template-columns: 1fr;
        grid-template-rows: auto;
      }}
      .k8s-cluster-cp {{ grid-row: auto; grid-column: 1; }}
      .k8s-cluster-bridge {{
        grid-row: auto;
        grid-column: 1;
        flex-direction: row;
        justify-content: center;
        gap: 24px;
      }}
      .k8s-cluster-workers {{ grid-row: auto; grid-column: 1; }}
    }}
    .k8s-table {{
      font-size: 0.72em !important;
      margin: 10px auto !important;
      border-collapse: collapse !important;
      max-width: 98% !important;
    }}
    .k8s-table th, .k8s-table td {{
      border: 1px solid rgba(255,255,255,0.2) !important;
      padding: 8px 10px !important;
    }}
    .k8s-table th {{
      background: rgba(50,108,229,0.25) !important;
      color: #7eb8ff !important;
    }}
    .k8s-quote {{
      background: linear-gradient(90deg, rgba(50,108,229,0.15), transparent);
      border-left: 4px solid #326CE5;
      padding: 10px 16px;
      margin: 8px 0;
      border-radius: 0 8px 8px 0;
      text-align: left !important;
      font-style: italic;
      color: #e6edf3 !important;
    }}
    .k8s-lead {{ color: #00d4aa !important; }}
    .fragment.visible {{
      animation: fragmentFadeIn 0.55s ease-out;
    }}
    @keyframes fragmentFadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
</head>
<body>
<div class="reveal"><div class="slides">

{sections_html}

</div></div>
<script src="{REVEAL_BASE}/js/reveal.min.js"></script>
<script src="{REVEAL_BASE}/js/notes.min.js"></script>
<script src="{REVEAL_BASE}/js/markdown.min.js"></script>
<script src="{REVEAL_BASE}/js/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({{
    startOnLoad: false,
    theme: 'dark',
    securityLevel: 'loose',
    fontFamily: 'trebuchet ms, verdana, sans-serif'
  }});

  Reveal.initialize({{
    hash: true,
    transition: 'slide',
    transitionSpeed: 'default',
    backgroundTransition: 'fade',
    controls: true,
    progress: true,
    slideNumber: 'c/t',
    center: true,
    margin: 0.04,
    fragments: true,
    plugins: [ RevealMarkdown, RevealHighlight, RevealNotes ]
  }});

  async function runMermaidOnSlide(slide) {{
    if (!slide) return;
    var nodes = slide.querySelectorAll('.mermaid:not([data-processed])');
    for (var i = 0; i < nodes.length; i++) {{
      try {{
        await mermaid.run({{ nodes: [nodes[i]] }});
        nodes[i].setAttribute('data-processed', 'true');
      }} catch (e) {{ console.warn(e); }}
    }}
  }}

  Reveal.on('ready', function() {{
    runMermaidOnSlide(Reveal.getCurrentSlide());
  }});
  Reveal.on('slidechanged', function(e) {{
    runMermaidOnSlide(e.currentSlide);
  }});
</script>
</body>
</html>"""

    OUT.write_text(html_doc, encoding="utf-8")
    print("Wrote", OUT, "slides:", len(sections) + 1)


if __name__ == "__main__":
    main()
