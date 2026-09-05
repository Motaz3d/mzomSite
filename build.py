#!/usr/bin/env python3
"""يبني الموقع من ملفات content/*.md إلى صفحات HTML ثابتة.

الاستخدام:
    python3 build.py

البنية الناتجة:
    index.html   — يعرض أحدث نص منشور كاملًا مباشرة + زر «تصفّح الكتاب كاملًا»
    book.html    — فهرس الكتاب: كل النصوص المنشورة بتواريخها
    pieces/*.html — صفحة كل نص، مع أزرار تنقّل (السابق/الكتاب/التالي)

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

BOOK_TITLE = "المهاجر — لقطات ومرايا"
BOOK_INTRO = (
    "قصص قصيرة جدًا تعبّر عن الوجع — من الحي اليهودي في دمشق "
    "إلى مقاهي لوكسمبورغ. يُنشر الكتاب هنا لقطة لقطة، نصًا جديدًا كل يوم."
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


def series_line(piece: dict) -> str:
    series = piece.get("series", "")
    number = piece.get("number", "")
    return series + (f" — {number}" if number else "")


def piece_url(piece: dict) -> str:
    return f"pieces/{piece['slug']}.html"


def piece_header(piece: dict) -> str:
    parts = ['<header class="piece-header">']
    line = series_line(piece)
    if line:
        parts.append(f'<p class="series">{html.escape(line)}</p>')
    parts.append(f"<h1>{html.escape(piece['title'])}</h1>")
    parts.append(
        f'<p class="meta">{ar_date(piece["date"])} — المقطع {html.escape(piece["kh"])}</p>'
    )
    parts.append("</header>")
    return "\n".join(parts)


def hero() -> str:
    return (
        '<section class="hero">'
        f'<h1 class="book-title">{BOOK_TITLE}</h1>'
        f'<p class="intro">{BOOK_INTRO}</p>'
        "</section>"
    )


def main() -> None:
    pieces = sorted(
        (parse_piece(p) for p in CONTENT.glob("*.md")),
        key=lambda m: m["date"],
    )

    PIECES_DIR.mkdir(exist_ok=True)

    for i, piece in enumerate(pieces):
        nav = ['<nav class="piece-nav">']
        if i > 0:
            nav.append(
                f'<a class="big-button" href="{piece_url(pieces[i - 1])}">→ النص السابق</a>'
            )
        nav.append('<a class="big-button secondary" href="../book.html">الكتاب كاملًا</a>')
        if i < len(pieces) - 1:
            nav.append(
                f'<a class="big-button" href="{piece_url(pieces[i + 1])}">النص التالي ←</a>'
            )
        nav.append("</nav>")

        body_html = (
            piece_header(piece)
            + f'\n<article class="piece-body">\n{md_to_html(piece["body"])}\n</article>\n'
            + "\n".join(nav)
        )
        line = series_line(piece)
        page = render(
            title=piece["title"],
            description=f"{line + ' — ' if line else ''}{piece['title']} — من كتاب «{BOOK_TITLE}»",
            content_html=body_html,
            root="../",
        )
        out = PIECES_DIR / f"{piece['slug']}.html"
        out.write_text(page, encoding="utf-8")
        print(f"بُني: pieces/{piece['slug']}.html")

    if pieces:
        latest = pieces[-1]
        latest_html = (
            piece_header(latest)
            + f'\n<article class="piece-body">\n{md_to_html(latest["body"])}\n</article>'
        )
        index_body = (
            hero()
            + "\n"
            + latest_html
            + '\n<div class="center"><a class="big-button" href="book.html">تصفّح الكتاب كاملًا ←</a></div>'
        )
    else:
        index_body = (
            hero()
            + '\n<p class="intro center-text">النص الأول قريبًا — يُعرض هنا كاملًا فور نشره، قبل أي مكان آخر.</p>'
        )
    index = render(
        title=BOOK_TITLE,
        description=f"كتاب «{BOOK_TITLE}» — يُنشر لقطة لقطة على موقع معتز عمرين",
        content_html=index_body,
        root="",
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    print("بُني: index.html")

    items = []
    for piece in reversed(pieces):
        line = series_line(piece)
        items.append(
            "<li>"
            + (f'<span class="series">{html.escape(line)}</span>' if line else "")
            + f'<a class="piece-title" href="{piece_url(piece)}">{html.escape(piece["title"])}</a>'
            + f'<span class="date">{ar_date(piece["date"])}</span>'
            + "</li>"
        )
    if items:
        book_body = hero() + '\n<ul class="pieces">\n' + "\n".join(items) + "\n</ul>"
    else:
        book_body = (
            hero()
            + '\n<p class="intro center-text">لا نصوص منشورة بعد — أول لقطة في الطريق.</p>'
        )
    book = render(
        title=f"الكتاب كاملًا — {BOOK_TITLE}",
        description=f"فهرس نصوص كتاب «{BOOK_TITLE}» المنشورة حتى الآن",
        content_html=book_body,
        root="",
    )
    (ROOT / "book.html").write_text(book, encoding="utf-8")
    print("بُني: book.html")


if __name__ == "__main__":
    main()
