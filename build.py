#!/usr/bin/env python3
"""يبني الموقع بعدّة لغات.

المصدر:
    content/*.md               — النصوص العربية المنشورة (الأصل)
    translations/<lang>/*.md   — ترجماتها (en, es, zh) بنفس تنسيق الترويسة ونفس slug.
                                 لا تُعرض الترجمة إلا إذا كان النص العربي منشورًا في content/.

الناتج:
    index.html, book.html, pieces/*.html                          — العربية (الجذر)
    <lang>/index.html, <lang>/book.html, <lang>/pieces/*.html     — الترجمات

كل ملف يبدأ بترويسة بصيغة:
    ---
    title: ...
    series: ...        (اختياري)
    number: ...        (اختياري — رقم الرسالة/الفصل داخل السلسلة)
    kh: خ-000          (رقم المقطع في ورشة الكتابة — يبقى كما هو في كل اللغات)
    slug: ascii-slug   (يصبح اسم الملف: pieces/<slug>.html)
    date: YYYY-MM-DD
    ---
    ثم النص. الفقرات تفصلها أسطر فارغة، **غامق** و*مائل* مدعومان.

الاستخدام:
    python3 build.py
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TRANSLATIONS = ROOT / "translations"
TEMPLATE = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")

SITE_URL = "https://motazomarien.com"

LANG_ORDER = ["ar", "en", "es", "zh"]

LANGS = {
    "ar": {
        "dir": "rtl",
        "label": "العربية",
        "site_name": "معتز عمرين",
        "tagline": "رواية بلا عنوان — عن الاغتراب",
        "book_title": "المهاجر — لقطات ومرايا",
        "book_intro": (
            "قصص قصيرة جدًا تعبّر عن الوجع — من الحي اليهودي في دمشق "
            "إلى مقاهي لوكسمبورغ. يُنشر الكتاب هنا لقطة لقطة، نصًا جديدًا كل يوم."
        ),
        "footer": "motazomarien.com — تُنشر النصوص تباعًا، كل يوم قصة",
        "prev": "→ النص السابق",
        "book_full": "الكتاب كاملًا",
        "next": "النص التالي ←",
        "browse": "تصفّح الكتاب كاملًا ←",
        "piece_word": "المقطع",
        "index_desc": "كتاب «{book}» — يُنشر لقطة لقطة على موقع {name}",
        "book_desc": "فهرس نصوص كتاب «{book}» المنشورة حتى الآن",
        "piece_desc": "{title} — من كتاب «{book}»",
        "book_page_title": "الكتاب كاملًا — {book}",
        "empty_index": "النص الأول قريبًا — يُعرض هنا كاملًا فور نشره، قبل أي مكان آخر.",
        "empty_book": "لا نصوص منشورة بعد — أول لقطة في الطريق.",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            "family=Amiri:ital,wght@0,400;0,700;1,400&"
            'family=Aref+Ruqaa:wght@400;700&display=swap" rel="stylesheet">'
        ),
    },
    "en": {
        "dir": "ltr",
        "label": "English",
        "site_name": "Motaz Omarien",
        "tagline": "An untitled novel — on estrangement",
        "book_title": "The Migrant — Snapshots and Mirrors",
        "book_intro": (
            "Very short stories that give voice to the ache — from the Jewish "
            "Quarter in Damascus to the cafés of Luxembourg. The book appears "
            "here snapshot by snapshot, one new text every day."
        ),
        "footer": "motazomarien.com — published in installments, a story every day",
        "prev": "← Previous piece",
        "book_full": "The full book",
        "next": "Next piece →",
        "browse": "Browse the full book →",
        "piece_word": "Piece",
        "index_desc": "The book “{book}” — serialized snapshot by snapshot on the site of {name}",
        "book_desc": "Index of the texts published so far from “{book}”",
        "piece_desc": "{title} — from the book “{book}”",
        "book_page_title": "The full book — {book}",
        "empty_index": "The first text is coming soon — it will appear here in full the moment it is published, before anywhere else.",
        "empty_book": "No texts published yet — the first snapshot is on its way.",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
        ),
    },
    "es": {
        "dir": "ltr",
        "label": "Español",
        "site_name": "Motaz Omarien",
        "tagline": "Una novela sin título — sobre la alienación",
        "book_title": "El emigrante — Instantáneas y espejos",
        "book_intro": (
            "Relatos muy breves que dan voz al dolor — del barrio judío de "
            "Damasco a los cafés de Luxemburgo. El libro se publica aquí "
            "instantánea a instantánea, un texto nuevo cada día."
        ),
        "footer": "motazomarien.com — publicación por entregas, una historia cada día",
        "prev": "← Texto anterior",
        "book_full": "El libro completo",
        "next": "Texto siguiente →",
        "browse": "Explorar el libro completo →",
        "piece_word": "Fragmento",
        "index_desc": "El libro «{book}» — publicación por entregas en el sitio de {name}",
        "book_desc": "Índice de los textos publicados hasta ahora de «{book}»",
        "piece_desc": "{title} — del libro «{book}»",
        "book_page_title": "El libro completo — {book}",
        "empty_index": "El primer texto llegará pronto — aparecerá aquí completo en cuanto se publique, antes que en ningún otro lugar.",
        "empty_book": "Aún no hay textos publicados — la primera instantánea está en camino.",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
        ),
    },
    "zh": {
        "dir": "ltr",
        "label": "中文",
        "site_name": "穆塔兹·奥马林",
        "tagline": "一部无名的小说——关于疏离",
        "book_title": "移民——剪影与镜像",
        "book_intro": (
            "极短的故事，诉说深处的伤痛——从大马士革的犹太区到卢森堡的咖啡馆。"
            "本书在此逐篇连载，每天一篇新文字。"
        ),
        "footer": "motazomarien.com——逐日连载，每天一个故事",
        "prev": "← 上一篇",
        "book_full": "全书目录",
        "next": "下一篇 →",
        "browse": "浏览全书 →",
        "piece_word": "片段",
        "index_desc": "《{book}》——在{name}的网站上逐篇连载",
        "book_desc": "《{book}》已发表作品目录",
        "piece_desc": "{title}——选自《{book}》",
        "book_page_title": "全书目录——《{book}》",
        "empty_index": "第一篇即将发布——将在发表当天第一时间完整呈现于此。",
        "empty_book": "尚未发表任何作品——第一幅剪影正在路上。",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=Noto+Serif+SC:wght@400;600&display=swap" rel="stylesheet">'
        ),
    },
}

MONTHS = {
    "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
           "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio",
           "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
}


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
    text = html.escape(text, quote=False)
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


def fmt_date(lang: str, iso: str) -> str:
    year, month, day = (int(part) for part in iso.split("-"))
    if lang == "ar":
        return f"{day} {MONTHS['ar'][month - 1]} {year}"
    if lang == "en":
        return f"{MONTHS['en'][month - 1]} {day}, {year}"
    if lang == "es":
        return f"{day} de {MONTHS['es'][month - 1]} de {year}"
    return f"{year}年{month}月{day}日"


def fmt_kh(lang: str, kh: str) -> str:
    return kh if lang == "ar" else kh.replace("خ", "kh")


def series_line(piece: dict) -> str:
    series = piece.get("series", "")
    number = piece.get("number", "")
    return series + (f" — {number}" if number else "")


def piece_path(piece: dict) -> str:
    return f"pieces/{piece['slug']}.html"


def lang_prefix(lang: str) -> str:
    return "" if lang == "ar" else f"{lang}/"


def switcher(lang: str, alt: dict, root: str) -> str:
    links = []
    for other in LANG_ORDER:
        label = LANGS[other]["label"]
        if other == lang:
            links.append(f'<a aria-current="true">{label}</a>')
        else:
            links.append(f'<a href="{root}{lang_prefix(other)}{alt[other]}">{label}</a>')
    return "\n      ".join(links)


def alternates(alt: dict) -> str:
    links = [
        f'<link rel="alternate" hreflang="{code}" href="{SITE_URL}/{lang_prefix(code)}{path}">'
        for code, path in alt.items()
    ]
    links.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{alt["ar"]}">'
    )
    return "\n  ".join(links)


def render(lang: str, title: str, description: str, content_html: str,
           root: str, home: str, alt: dict) -> str:
    strings = LANGS[lang]
    return (
        TEMPLATE.replace("{{lang}}", lang)
        .replace("{{dir}}", strings["dir"])
        .replace("{{title}}", html.escape(title))
        .replace("{{description}}", html.escape(description))
        .replace("{{sitename}}", strings["site_name"])
        .replace("{{tagline}}", strings["tagline"])
        .replace("{{footer}}", strings["footer"])
        .replace("{{fonts}}", strings["fonts"])
        .replace("{{alternates}}", alternates(alt))
        .replace("{{langs}}", switcher(lang, alt, root))
        .replace("{{root}}", root)
        .replace("{{home}}", home)
        .replace("{{content}}", content_html)
    )


def piece_header(lang: str, piece: dict) -> str:
    strings = LANGS[lang]
    parts = ['<header class="piece-header">']
    line = series_line(piece)
    if line:
        parts.append(f'<p class="series">{html.escape(line)}</p>')
    parts.append(f"<h1>{html.escape(piece['title'])}</h1>")
    parts.append(
        f'<p class="meta">{fmt_date(lang, piece["date"])} — '
        f'{strings["piece_word"]} {fmt_kh(lang, piece["kh"])}</p>'
    )
    parts.append("</header>")
    return "\n".join(parts)


def hero(lang: str) -> str:
    strings = LANGS[lang]
    return (
        '<section class="hero">'
        f'<h1 class="book-title">{strings["book_title"]}</h1>'
        f'<p class="intro">{strings["book_intro"]}</p>'
        "</section>"
    )


def build_lang(lang: str, pieces: list, published_slugs: set) -> None:
    strings = LANGS[lang]
    out_root = ROOT if lang == "ar" else ROOT / lang
    pieces_dir = out_root / "pieces"
    pieces_dir.mkdir(parents=True, exist_ok=True)

    def alt_for(canonical: str) -> dict:
        return {code: canonical for code in LANG_ORDER}

    for i, piece in enumerate(pieces):
        nav = ['<nav class="piece-nav">']
        if i > 0:
            nav.append(
                f'<a class="big-button" href="{piece_path(pieces[i - 1])}">{strings["prev"]}</a>'
            )
        nav.append(
            f'<a class="big-button secondary" href="../book.html">{strings["book_full"]}</a>'
        )
        if i < len(pieces) - 1:
            nav.append(
                f'<a class="big-button" href="{piece_path(pieces[i + 1])}">{strings["next"]}</a>'
            )
        nav.append("</nav>")

        body_html = (
            piece_header(lang, piece)
            + f'\n<article class="piece-body" lang="{lang}">\n{md_to_html(piece["body"])}\n</article>\n'
            + "\n".join(nav)
        )
        canonical = piece_path(piece)
        alt = {}
        for code in LANG_ORDER:
            if code == "ar" or piece["slug"] in published_slugs.get(code, set()):
                alt[code] = canonical
            else:
                alt[code] = "index.html"
        line = series_line(piece)
        desc = strings["piece_desc"].format(
            title=(line + " — " if line else "") + piece["title"],
            book=strings["book_title"],
        )
        root = "../" if lang == "ar" else "../../"
        page = render(
            lang,
            title=piece["title"],
            description=desc,
            content_html=body_html,
            root=root,
            home="../index.html",
            alt=alt,
        )
        out = pieces_dir / f"{piece['slug']}.html"
        out.write_text(page, encoding="utf-8")
        print(f"بُني: {lang_prefix(lang)}{canonical}")

    root = "" if lang == "ar" else "../"
    if pieces:
        latest = pieces[-1]
        index_body = (
            hero(lang)
            + "\n"
            + piece_header(lang, latest)
            + f'\n<article class="piece-body" lang="{lang}">\n{md_to_html(latest["body"])}\n</article>'
            + f'\n<div class="center"><a class="big-button" href="book.html">{strings["browse"]}</a></div>'
        )
    else:
        index_body = (
            hero(lang)
            + f'\n<p class="intro center-text">{strings["empty_index"]}</p>'
        )
    index = render(
        lang,
        title=strings["book_title"],
        description=strings["index_desc"].format(
            book=strings["book_title"], name=strings["site_name"]
        ),
        content_html=index_body,
        root=root,
        home="index.html",
        alt=alt_for("index.html"),
    )
    (out_root / "index.html").write_text(index, encoding="utf-8")
    print(f"بُني: {lang_prefix(lang)}index.html")

    items = []
    for piece in reversed(pieces):
        line = series_line(piece)
        items.append(
            "<li>"
            + (f'<span class="series">{html.escape(line)}</span>' if line else "")
            + f'<a class="piece-title" href="{piece_path(piece)}">{html.escape(piece["title"])}</a>'
            + f'<span class="date">{fmt_date(lang, piece["date"])}</span>'
            + "</li>"
        )
    if items:
        book_body = hero(lang) + '\n<ul class="pieces">\n' + "\n".join(items) + "\n</ul>"
    else:
        book_body = hero(lang) + f'\n<p class="intro center-text">{strings["empty_book"]}</p>'
    book = render(
        lang,
        title=strings["book_page_title"].format(book=strings["book_title"]),
        description=strings["book_desc"].format(book=strings["book_title"]),
        content_html=book_body,
        root=root,
        home="index.html",
        alt=alt_for("book.html"),
    )
    (out_root / "book.html").write_text(book, encoding="utf-8")
    print(f"بُني: {lang_prefix(lang)}book.html")


def main() -> None:
    ar_pieces = sorted(
        (parse_piece(p) for p in CONTENT.glob("*.md")),
        key=lambda m: (m["date"], int(re.search(r"\d+", m["kh"]).group())),
    )
    ar_slugs = {p["slug"] for p in ar_pieces}

    translated = {}   # lang -> قائمة القطع المترجمة بترتيب العربية
    published = {}    # lang -> مجموعة الـ slugs المتوفرة
    for lang in LANG_ORDER[1:]:
        by_slug = {}
        lang_dir = TRANSLATIONS / lang
        if lang_dir.is_dir():
            for path in lang_dir.glob("*.md"):
                meta = parse_piece(path)
                by_slug[meta["slug"]] = meta
        published[lang] = set(by_slug) & ar_slugs
        translated[lang] = [by_slug[p["slug"]] for p in ar_pieces if p["slug"] in by_slug]

    build_lang("ar", ar_pieces, published)
    for lang in LANG_ORDER[1:]:
        build_lang(lang, translated[lang], published)


if __name__ == "__main__":
    main()
