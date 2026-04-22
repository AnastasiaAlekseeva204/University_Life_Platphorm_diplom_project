# -*- coding: utf-8 -*-
"""dipoma/presa.md -> myplatform/templates/presentation_reveal.html (Reveal.js).

Стили и скрипты копируются из PRESA/css и PRESA/js в myproject/static/presa/
и подключаются как /static/presa/... (STATIC_URL по умолчанию /static/).

Формат слайдов в presa.md: строки вида «### Слайд N. Заголовок».
"""
from __future__ import annotations

import importlib.util
import re
import shutil
from pathlib import Path

PRESA_DIR = Path(__file__).resolve().parent
ROOT = PRESA_DIR.parent
MD_PATH = ROOT / "dipoma" / "presa.md"
STATIC_OUT = ROOT / "myproject" / "static" / "presa"
TEMPLATE_OUT = ROOT / "myproject" / "myplatform" / "templates" / "presentation_reveal.html"

TRANSITIONS = ("slide", "fade", "convex", "zoom", "slide")

# Фон слайда + цвета «нейросети» (узлы / связи / сетка), коррелирующие с фоном.
SLIDE_THEMES = (
    {
        "bg": "#0d1117",
        "na": "rgba(59,130,246,0.7)",
        "nb": "rgba(34,211,238,0.55)",
        "nc": "rgba(167,139,250,0.5)",
        "nd": "rgba(96,165,250,0.22)",
    },
    {
        "bg": "#111827",
        "na": "rgba(99,102,241,0.65)",
        "nb": "rgba(56,189,248,0.55)",
        "nc": "rgba(244,114,182,0.4)",
        "nd": "rgba(129,140,248,0.2)",
    },
    {
        "bg": "#0f172a",
        "na": "rgba(96,165,250,0.68)",
        "nb": "rgba(45,212,191,0.52)",
        "nc": "rgba(147,197,253,0.45)",
        "nd": "rgba(56,189,248,0.18)",
    },
    {
        "bg": "#1e1b4b",
        "na": "rgba(139,92,246,0.7)",
        "nb": "rgba(244,114,182,0.5)",
        "nc": "rgba(196,181,253,0.45)",
        "nd": "rgba(167,139,250,0.2)",
    },
    {
        "bg": "#0c4a6e",
        "na": "rgba(125,211,252,0.72)",
        "nb": "rgba(103,232,249,0.55)",
        "nc": "rgba(56,189,248,0.5)",
        "nd": "rgba(14,165,233,0.25)",
    },
    {
        "bg": "#134e4a",
        "na": "rgba(52,211,153,0.7)",
        "nb": "rgba(163,230,53,0.45)",
        "nc": "rgba(110,231,183,0.5)",
        "nd": "rgba(45,212,191,0.22)",
    },
)

TITLE_NEURAL_STYLE = (
    "--na: rgba(0,91,255,0.55); "
    "--nb: rgba(126,184,255,0.5); "
    "--nc: rgba(0,212,170,0.42); "
    "--nd: rgba(0,91,255,0.15);"
)


def _load_k8s_builder():
    path = PRESA_DIR / "build_lect_k8s_net_gitops_reveal.py"
    spec = importlib.util.spec_from_file_location("k8s_build", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def esc(s: str) -> str:
    import html

    return html.escape(s, quote=True)


def strip_fragment_classes_from_html(html: str) -> str:
    """Удаляет fragment / fade-in-then-semi-out из class (presentation.css + Reveal скрывают их)."""

    def _open_tag(m: re.Match) -> str:
        tag, sp, val, sp2 = m.group(1), m.group(2), m.group(3), m.group(4)
        if "fragment" not in val:
            return m.group(0)
        parts = [p for p in val.split() if p not in ("fragment", "fade-in-then-semi-out")]
        if not parts:
            return f"<{tag}>"
        return f"<{tag}{sp}class=\"{' '.join(parts)}\"{sp2}>"

    # <li class="..."> — пробел перед class обязателен, иначе прежний regex не срабатывал
    return re.sub(r"<(\w+)(\s+)class=\"([^\"]*)\"(\s*)>", _open_tag, html)


def strip_block_headers_and_speaker_lines(body: str) -> str:
    """Из тела слайда убираем заголовки «## Блок …» и реплики «*Устно:* …» (presa.md не меняем)."""
    out_lines: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if re.match(r"^##\s+Блок\b", s):
            continue
        if re.match(r"^\*Устно:\*", s) or re.match(r"^Устно:", s):
            continue
        out_lines.append(line)
    text = "\n".join(out_lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_slides_presa(md: str) -> list[tuple[str, str]]:
    """Разбиение по «### Слайд N. …»."""
    parts = re.split(r"(?m)^(###\s+Слайд\s+\d+\..+)$", md)
    slides: list[tuple[str, str]] = []
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
        title_line = parts[i].strip()
        body = parts[i + 1]
        slides.append((title_line, body))
    return slides


def copy_reveal_assets():
    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    for name in ("reveal.min.css", "black.min.css", "monokai.min.css"):
        src = PRESA_DIR / "css" / name
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, STATIC_OUT / name)
    # presentation.css скрывает .fragment (opacity:0) — для этой презентации не копируем и не подключаем
    for name in ("reveal.min.js", "notes.min.js", "markdown.min.js", "highlight.min.js"):
        src = PRESA_DIR / "js" / name
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, STATIC_OUT / name)


def main() -> None:
    b = _load_k8s_builder()
    slide_body_to_html = b.slide_body_to_html

    raw = MD_PATH.read_text(encoding="utf-8")
    slide_pairs = split_slides_presa(raw)
    if not slide_pairs:
        raise SystemExit(f"No slides found in {MD_PATH} (expected lines «### Слайд N. …»)")

    sections: list[str] = []
    for idx, (title_line, body) in enumerate(slide_pairs):
        m = re.match(r"^###\s+(Слайд\s+\d+)\.\s*(.+)$", title_line.strip())
        if not m:
            continue
        num, title = m.group(1), m.group(2).strip()
        h2 = f"{num}. {title}"
        trans = TRANSITIONS[idx % len(TRANSITIONS)]
        theme = SLIDE_THEMES[idx % len(SLIDE_THEMES)]
        bg = theme["bg"]
        neural_style = (
            f"--na: {theme['na']}; --nb: {theme['nb']}; "
            f"--nc: {theme['nc']}; --nd: {theme['nd']};"
        )
        body = strip_block_headers_and_speaker_lines(body)
        body_lines = body.rstrip().split("\n")
        while body_lines and body_lines[-1].strip() == "---":
            body_lines.pop()
        inner = strip_fragment_classes_from_html(slide_body_to_html("\n".join(body_lines)))
        sections.append(
            f"""<section data-transition="{trans}" data-background-color="{bg}" class="k8s-slide" style="{neural_style}">
  <h2>{esc(h2)}</h2>
  <div class="k8s-slide-inner">
{inner}
  </div>
</section>"""
        )

    n_slides = len(sections) + 1
    title_slide = f"""<section data-transition="zoom" data-background-gradient="linear-gradient(135deg,#05122d 0%,#0a2e79 45%,#005bff 100%)" class="k8s-title-slide" style="{TITLE_NEURAL_STYLE}">
  <div class="k8s-title-card">
    <div class="k8s-helm" aria-hidden="true">🎓</div>
    <h1 class="k8s-title-h1">ВКР · Веб-платформа МПГУ</h1>
    <p class="k8s-title-sub">Внеучебная деятельность: анонсы, учёт, Django</p>
  </div>
</section>"""

    sections_html = "\n\n".join([title_slide] + sections)

    # Тот же инлайн-стиль, что в build_lect_k8s…, но пути к CSS/JS — из STATIC_PREFIX
    html_doc = f"""{{% load static %}}
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Презентация ВКР — МПГУ</title>
  <link rel="stylesheet" href="{{% static 'presa/reveal.min.css' %}}">
  <link rel="stylesheet" href="{{% static 'presa/black.min.css' %}}">
  <link rel="stylesheet" href="{{% static 'presa/monokai.min.css' %}}">
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
    .reveal .slides section.k8s-slide {{
      overflow-y: auto !important;
      justify-content: center !important;
      padding-top: 12px !important;
      padding-bottom: 12px !important;
    }}
    .k8s-slide, .k8s-title-slide {{
      position: relative !important;
    }}
    /* Псевдоэлементы: не участвуют во flex Reveal, не ломают вертикальное центрирование */
    .k8s-slide::before, .k8s-title-slide::before {{
      content: "";
      position: absolute;
      inset: -10%;
      z-index: -1;
      pointer-events: none;
      background-image:
        radial-gradient(circle at 10% 20%, var(--na) 0 3px, transparent 4px),
        radial-gradient(circle at 82% 14%, var(--nb) 0 2.5px, transparent 3.5px),
        radial-gradient(circle at 38% 78%, var(--nc) 0 3px, transparent 4px),
        radial-gradient(circle at 90% 55%, var(--na) 0 2px, transparent 3px),
        radial-gradient(circle at 22% 90%, var(--nb) 0 2.5px, transparent 3.5px),
        radial-gradient(circle at 58% 42%, var(--nc) 0 2px, transparent 3px),
        radial-gradient(circle at 70% 82%, var(--na) 0 2px, transparent 3px);
      background-size: 100% 100%;
      opacity: 0.55;
      animation: neuralNodesPulse 9s ease-in-out infinite;
    }}
    .k8s-slide::after, .k8s-title-slide::after {{
      content: "";
      position: absolute;
      inset: 0;
      z-index: -1;
      pointer-events: none;
      mix-blend-mode: screen;
      background-image:
        linear-gradient(112deg, transparent 46%, var(--nd) 48.5%, var(--nd) 51.5%, transparent 54%),
        linear-gradient(28deg, transparent 45%, var(--nd) 47.5%, var(--nd) 52.5%, transparent 55%),
        linear-gradient(154deg, transparent 48%, var(--nd) 49.8%, var(--nd) 50.2%, transparent 52%),
        linear-gradient(90deg, var(--nd) 1px, transparent 1px),
        linear-gradient(0deg, var(--nd) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 100% 100%, 88px 88px, 88px 88px;
      background-position: 0 0, 0 0, 0 0, 0 0, 0 0;
      opacity: 0.55;
      animation: neuralMeshShift 20s linear infinite;
    }}
    .k8s-title-slide::before {{ opacity: 0.4; }}
    .k8s-title-slide::after {{ opacity: 0.45; }}
    @keyframes neuralNodesPulse {{
      0%, 100% {{ opacity: 0.45; filter: brightness(1); }}
      50% {{ opacity: 0.72; filter: brightness(1.12); }}
    }}
    @keyframes neuralMeshShift {{
      0% {{ background-position: 0 0, 0 0, 0 0, 0 0, 0 0; opacity: 0.5; }}
      50% {{ background-position: 8% -5%, -6% 4%, 4% 7%, 36px 22px, -24px 40px; opacity: 0.75; }}
      100% {{ background-position: 0 0, 0 0, 0 0, 72px 64px, 48px -40px; opacity: 0.5; }}
    }}
    .k8s-slide > h2 {{
      position: relative;
      z-index: 1;
      flex-shrink: 0;
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
      position: relative;
      z-index: 1;
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
      position: relative;
      z-index: 1;
      width: 100%;
      max-width: 100%;
      min-height: 0;
      flex-shrink: 0;
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
    /* Генератор из lect_k8s помечает пункты как .fragment — без показа по шагам текст «пропадает» */
    .reveal .slides section .fragment {{
      opacity: 1 !important;
      visibility: visible !important;
      transform: none !important;
    }}
  </style>
</head>
<body>
<div class="reveal"><div class="slides">

{sections_html}

</div></div>
<script src="{{% static 'presa/reveal.min.js' %}}"></script>
<script src="{{% static 'presa/notes.min.js' %}}"></script>
<script src="{{% static 'presa/markdown.min.js' %}}"></script>
<script src="{{% static 'presa/highlight.min.js' %}}"></script>
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
    fragments: false,
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
    document.querySelectorAll('.reveal .slides section .fragment').forEach(function(el) {{
      el.classList.add('visible');
    }});
    runMermaidOnSlide(Reveal.getCurrentSlide());
  }});
  Reveal.on('slidechanged', function(e) {{
    e.currentSlide.querySelectorAll('.fragment').forEach(function(el) {{
      el.classList.add('visible');
    }});
    runMermaidOnSlide(e.currentSlide);
  }});
</script>
</body>
</html>"""

    copy_reveal_assets()
    TEMPLATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATE_OUT.write_text(html_doc, encoding="utf-8")
    print("Wrote", TEMPLATE_OUT)
    print("Copied Reveal assets to", STATIC_OUT)
    print("Content slides:", len(sections), "+ title =", n_slides)


if __name__ == "__main__":
    main()
