#!/usr/bin/env python3
"""يبني الموقع من ملفات content/*.md إلى صفحات HTML ثابتة.

الاستخدام:
    python3 build.py

كل ملف في content/ يبدأ بترويسة بصيغة:
    ---
    title: ...
    series: ...        (اختياري)
    number: ...        (اختياري — رقم الرسالة/الفصل داخل السلسلة)
    kh: خ-000          (رقم المقطع في ورشة الكتابة)
    slug: ascii-slug   (يصبح اسم الملف: pieces/<slug>.html)
    date: YYYY-MM-DD
    ---
    ثم النص. الفقرات تفصلها أسطر فارغة، **غامق** و*مائل* مدعومان.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TEMPLATE = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")
PIECES_DIR = ROOT / "pieces"

SITE_NAME = "معتز عمرين"
INTRO = (
    "هنا تُنشر تباعًا أجزاء من رواية بلا عنوان عن الاغتراب: "
    "تفتتحها سلسلة «رسائل إلى مارينا»، وتلحق بها مشاهد ونصوص من المسار نفسه. "
    "كل يوم قصة."
)

AR_MONTHS = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
]


def parse_piece(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError(f"ترويسة مفقودة في {path.name}")
    meta_raw, body = match.groups()
    meta = {}
    for line in meta_raw.splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for required in ("title", "kh", "slug", "date"):
        if required not in meta:
            raise ValueError(f"الحقل {required} مفقود في {path.name}")
    meta["body"] = body.strip()
    return meta


def md_inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    return text


def md_to_html(md: str) -> str:
    blocks = re.split(r"\n\s*\n", md.strip())
    out = []
    for block in blocks:
        if block.startswith("### "):
            out.append(f"<h3>{md_inline(block[4:])}</h3>")
        elif block.startswith("## "):
            out.append(f"<h2>{md_inline(block[3:])}</h2>")
        else:
            out.append(f"<p>{md_inline(block)}</p>")
    return "\n".join(out)


def ar_date(iso: str) -> str:
    year, month, day = (int(part) for part in iso.split("-"))
    return f"{day} {AR_MONTHS[month - 1]} {year}"


def render(title: str, description: str, content_html: str, root: str) -> str:
    return (
        TEMPLATE.replace("{{title}}", html.escape(title))
        .replace("{{description}}", html.escape(description))
        .replace("{{content}}", content_html)
        .replace("{{root}}", root)
    )


def main() -> None:
    pieces = sorted(
        (parse_piece(p) for p in CONTENT.glob("*.md")),
        key=lambda m: m["date"],
        reverse=True,
    )

    PIECES_DIR.mkdir(exist_ok=True)
    for piece in pieces:
        series = piece.get("series", "")
        number = piece.get("number", "")
        series_line = series + (f" — {number}" if number else "")
        header = ['<header class="piece-header">']
        if series_line:
            header.append(f'<p class="series">{html.escape(series_line)}</p>')
        header.append(f"<h1>{html.escape(piece['title'])}</h1>")
        header.append(
            f'<p class="meta">{ar_date(piece["date"])} — المقطع {html.escape(piece["kh"])}</p>'
        )
        header.append("</header>")
        body_html = (
            "\n".join(header)
            + f'\n<article class="piece-body">\n{md_to_html(piece["body"])}\n</article>'
            + f'\n<a class="back-link" href="../index.html">→ كل المنشور</a>'
        )
        page = render(
            title=piece["title"],
            description=f"{series_line + ' — ' if series_line else ''}{piece['title']} — نص من رواية بلا عنوان",
            content_html=body_html,
            root="../",
        )
        out = PIECES_DIR / f"{piece['slug']}.html"
        out.write_text(page, encoding="utf-8")
        print(f"بُني: pieces/{piece['slug']}.html")

    items = []
    for piece in pieces:
        series = piece.get("series", "")
        number = piece.get("number", "")
        series_line = series + (f" — رسالة {number}" if number else "")
        items.append(
            "<li>"
            + (f'<span class="series">{html.escape(series_line)}</span>' if series_line else "")
            + f'<a class="piece-title" href="pieces/{piece["slug"]}.html">{html.escape(piece["title"])}</a>'
            + f'<span class="date">{ar_date(piece["date"])}</span>'
            + "</li>"
        )
    if items:
        index_body = (
            f'<p class="intro">{INTRO}</p>\n<ul class="pieces">\n'
            + "\n".join(items)
            + "\n</ul>"
        )
    else:
        index_body = f'<p class="intro">{INTRO}</p>\n<p class="intro">لا منشور حاليًا — قريبًا.</p>'
    index = render(
        title="الرئيسية",
        description="رواية بلا عنوان عن الاغتراب — تُنشر أجزاؤها تباعًا",
        content_html=index_body,
        root="",
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("بُني: index.html")


if __name__ == "__main__":
    main()
