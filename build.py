#!/usr/bin/env python3
"""يبني الموقع بعدّة لغات.

المصدر:
    content/*.md               — النصوص العربية المنشورة (الأصل)
    translations/<lang>/*.md   — ترجماتها (en, es, zh) بنفس تنسيق الترويسة ونفس slug.
                                 لا تُعرض الترجمة إلا إذا كان النص العربي منشورًا في content/.

الناتج:
    index.html, book.html, pieces/*.html                          — العربية (الجذر)
    <lang>/index.html, <lang>/book.html, <lang>/pieces/*.html     — الترجمات
    sitemap.xml                                                   — خريطة الموقع بكل اللغات (hreflang)

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
from urllib.parse import quote

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
TRANSLATIONS = ROOT / "translations"
TEMPLATE = (ROOT / "templates" / "base.html").read_text(encoding="utf-8")

SITE_URL = "https://motazomarien.com"

# خدمات التفاعل الخارجية — تُفعَّل بلصق القيمة هنا ثم إعادة البناء (python3 build.py).
# القسم المقابل يظهر في الموقع فقط بعد لصق قيمته:
WEB3FORMS_ACCESS_KEY = ""    # تعليقات القراء → بريد الكاتب — المفتاح من web3forms.com (تدخل بريدك فيصلك المفتاح فورًا)
NEWSLETTER_FORM_ACTION = ""  # نموذج الاشتراك البريدي — رابط النموذج المضمّن من Mailchimp (Audience → Signup forms → Embedded forms)
WHATSAPP_CHANNEL_URL = ""    # رابط قناة واتساب — تُنشأ من تطبيق واتساب (التحديثات ← القنوات ← إنشاء قناة)

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
        "piece_word": "لقطة",
        "index_desc": "كتاب «{book}» — يُنشر لقطة لقطة على موقع {name}",
        "book_desc": "فهرس نصوص كتاب «{book}» المنشورة حتى الآن",
        "piece_desc": "{title} — من كتاب «{book}»",
        "book_page_title": "الكتاب كاملًا — {book}",
        "empty_index": "النص الأول قريبًا — يُعرض هنا كاملًا فور نشره، قبل أي مكان آخر.",
        "empty_book": "لا نصوص منشورة بعد — أول لقطة في الطريق.",
        "share_wa": "شارك النص عبر واتساب",
        "comment_title": "تعليقك يصل إلى الكاتب",
        "comment_note": "اترك اسمك وبريدك وتعليقك — يصل مباشرة إلى بريد الكاتب، ولا يُنشر علنًا.",
        "comment_name": "الاسم",
        "comment_email": "البريد الإلكتروني",
        "comment_msg": "تعليقك…",
        "comment_send": "أرسل",
        "comment_subject": "تعليق على: {title}",
        "news_title": "يصلك نص اليوم",
        "news_note": "اشترك ببريدك ليصلك كل نص جديد يوم نشره، أو تابع قناة واتساب.",
        "news_button": "اشترك",
        "news_email": "بريدك الإلكتروني",
        "wa_channel": "تابع قناة واتساب ←",
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
        "piece_word": "Snapshot",
        "index_desc": "The book “{book}” — serialized snapshot by snapshot on the site of {name}",
        "book_desc": "Index of the texts published so far from “{book}”",
        "piece_desc": "{title} — from the book “{book}”",
        "book_page_title": "The full book — {book}",
        "empty_index": "The first text is coming soon — it will appear here in full the moment it is published, before anywhere else.",
        "empty_book": "No texts published yet — the first snapshot is on its way.",
        "share_wa": "Share this piece on WhatsApp",
        "comment_title": "Your comment reaches the author",
        "comment_note": "Leave your name, email, and comment — it goes straight to the author's inbox; nothing is published publicly.",
        "comment_name": "Name",
        "comment_email": "Email",
        "comment_msg": "Your comment…",
        "comment_send": "Send",
        "comment_subject": "Comment on: {title}",
        "news_title": "Get the day's text",
        "news_note": "Subscribe with your email to receive each new text on publication day, or follow the WhatsApp channel.",
        "news_button": "Subscribe",
        "news_email": "Your email",
        "wa_channel": "Follow the WhatsApp channel →",
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
        "piece_word": "Instantánea",
        "index_desc": "El libro «{book}» — publicación por entregas en el sitio de {name}",
        "book_desc": "Índice de los textos publicados hasta ahora de «{book}»",
        "piece_desc": "{title} — del libro «{book}»",
        "book_page_title": "El libro completo — {book}",
        "empty_index": "El primer texto llegará pronto — aparecerá aquí completo en cuanto se publique, antes que en ningún otro lugar.",
        "empty_book": "Aún no hay textos publicados — la primera instantánea está en camino.",
        "share_wa": "Compartir este texto por WhatsApp",
        "comment_title": "Tu comentario llega al autor",
        "comment_note": "Deja tu nombre, correo y comentario — llega directamente al buzón del autor; nada se publica en abierto.",
        "comment_name": "Nombre",
        "comment_email": "Correo electrónico",
        "comment_msg": "Tu comentario…",
        "comment_send": "Enviar",
        "comment_subject": "Comentario sobre: {title}",
        "news_title": "Recibe el texto del día",
        "news_note": "Suscríbete con tu correo para recibir cada texto nuevo el día de su publicación, o sigue el canal de WhatsApp.",
        "news_button": "Suscribirme",
        "news_email": "Tu correo electrónico",
        "wa_channel": "Seguir el canal de WhatsApp →",
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
        "piece_word": "剪影",
        "index_desc": "《{book}》——在{name}的网站上逐篇连载",
        "book_desc": "《{book}》已发表作品目录",
        "piece_desc": "{title}——选自《{book}》",
        "book_page_title": "全书目录——《{book}》",
        "empty_index": "第一篇即将发布——将在发表当天第一时间完整呈现于此。",
        "empty_book": "尚未发表任何作品——第一幅剪影正在路上。",
        "share_wa": "通过 WhatsApp 分享本文",
        "comment_title": "您的评论将直达作者",
        "comment_note": "留下您的姓名、邮箱和评论——评论直接发送到作者邮箱，不会公开发布。",
        "comment_name": "姓名",
        "comment_email": "电子邮箱",
        "comment_msg": "您的评论…",
        "comment_send": "发送",
        "comment_subject": "评论：{title}",
        "news_title": "每天接收新文章",
        "news_note": "留下邮箱订阅，发表当天即可收到新文章；或关注 WhatsApp 频道。",
        "news_button": "订阅",
        "news_email": "您的邮箱",
        "wa_channel": "关注 WhatsApp 频道 →",
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


def piece_header(lang: str, piece: dict, num: int) -> str:
    strings = LANGS[lang]
    parts = ['<header class="piece-header">']
    line = series_line(piece)
    if line:
        parts.append(f'<p class="series">{html.escape(line)}</p>')
    parts.append(f"<h1>{html.escape(piece['title'])}</h1>")
    parts.append(
        f'<p class="meta">{fmt_date(lang, piece["date"])} — '
        f'{strings["piece_word"]} {num}</p>'
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


def share_url(lang: str, piece: dict) -> str:
    # http مؤقتًا حتى تصدر شهادة HTTPS — يتحوّل الرابط تلقائيًا بعد تفعيلها
    url = f"http://motazomarien.com/{lang_prefix(lang)}{piece_path(piece)}"
    return f"https://wa.me/?text={quote(piece['title'] + ' — ' + url)}"


def interact_section(lang: str, piece: dict) -> str:
    strings = LANGS[lang]
    parts = ['<section class="interact">']
    parts.append(
        f'<p class="center"><a class="big-button secondary" '
        f'href="{share_url(lang, piece)}" target="_blank" rel="noopener">'
        f'{strings["share_wa"]}</a></p>'
    )
    if WEB3FORMS_ACCESS_KEY:
        subject = strings["comment_subject"].format(title=piece["title"])
        parts.append(
            f'<h2 class="interact-title">{strings["comment_title"]}</h2>\n'
            f'<p class="interact-note">{strings["comment_note"]}</p>\n'
            '<form class="comment-form" action="https://api.web3forms.com/submit" method="POST">\n'
            f'  <input type="hidden" name="access_key" value="{WEB3FORMS_ACCESS_KEY}">\n'
            f'  <input type="hidden" name="subject" value="{html.escape(subject)}">\n'
            f'  <input type="text" name="name" placeholder="{strings["comment_name"]}" required>\n'
            f'  <input type="email" name="email" placeholder="{strings["comment_email"]}" required>\n'
            f'  <textarea name="message" rows="4" placeholder="{strings["comment_msg"]}" required></textarea>\n'
            '  <input type="checkbox" name="botcheck" class="botcheck" tabindex="-1" autocomplete="off">\n'
            f'  <button type="submit" class="big-button">{strings["comment_send"]}</button>\n'
            "</form>"
        )
    parts.append("</section>")
    return "\n".join(parts)


def subscribe_section(lang: str) -> str:
    if not NEWSLETTER_FORM_ACTION and not WHATSAPP_CHANNEL_URL:
        return ""
    strings = LANGS[lang]
    parts = [
        '<section class="subscribe">',
        f'<h2 class="interact-title">{strings["news_title"]}</h2>',
        f'<p class="interact-note">{strings["news_note"]}</p>',
    ]
    if NEWSLETTER_FORM_ACTION:
        parts.append(
            f'<form class="subscribe-form" action="{NEWSLETTER_FORM_ACTION}" method="post" target="_blank">\n'
            f'  <input type="email" name="EMAIL" placeholder="{strings["news_email"]}" required>\n'
            f'  <button type="submit" class="big-button">{strings["news_button"]}</button>\n'
            "</form>"
        )
    if WHATSAPP_CHANNEL_URL:
        parts.append(
            f'<p class="center"><a class="big-button secondary" href="{WHATSAPP_CHANNEL_URL}" '
            f'target="_blank" rel="noopener">{strings["wa_channel"]}</a></p>'
        )
    parts.append("</section>")
    return "\n".join(parts)


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
            piece_header(lang, piece, i + 1)
            + f'\n<article class="piece-body" lang="{lang}">\n{md_to_html(piece["body"])}\n</article>\n'
            + "\n".join(nav)
            + "\n"
            + interact_section(lang, piece)
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
            + piece_header(lang, latest, len(pieces))
            + f'\n<article class="piece-body" lang="{lang}">\n{md_to_html(latest["body"])}\n</article>'
            + f'\n<div class="center"><a class="big-button" href="book.html">{strings["browse"]}</a></div>'
            + "\n"
            + subscribe_section(lang)
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
        book_body = (
            hero(lang)
            + '\n<ul class="pieces">\n'
            + "\n".join(items)
            + "\n</ul>\n"
            + subscribe_section(lang)
        )
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

    build_sitemap(ar_pieces, published)
    build_feed(ar_pieces)


def build_feed(ar_pieces: list) -> None:
    from datetime import datetime, timezone

    items = []
    for piece in reversed(ar_pieces[-20:]):
        link = f"{SITE_URL}/{piece_path(piece)}"
        year, month, day = (int(part) for part in piece["date"].split("-"))
        pub = datetime(year, month, day, 8, tzinfo=timezone.utc).strftime(
            "%a, %d %b %Y %H:%M:%S %z"
        )
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(piece['title'])}</title>\n"
            f"    <link>{link}</link>\n"
            f'    <guid isPermaLink="true">{link}</guid>\n'
            f"    <pubDate>{pub}</pubDate>\n"
            f"    <description><![CDATA[{md_to_html(piece['body'])}]]></description>\n"
            "  </item>"
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n<channel>\n'
        f"  <title>{html.escape(LANGS['ar']['site_name'])} — "
        f"{html.escape(LANGS['ar']['book_title'])}</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        f"  <description>{html.escape(LANGS['ar']['book_intro'])}</description>\n"
        "  <language>ar</language>\n"
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print("بُني: feed.xml")


def sitemap_url(canonical: str, alt: dict, lastmod: str) -> str:
    lines = [
        "  <url>",
        f"    <loc>{SITE_URL}/{html.escape(canonical)}</loc>",
    ]
    for code, path in alt.items():
        lines.append(
            f'    <xhtml:link rel="alternate" hreflang="{code}" '
            f'href="{SITE_URL}/{lang_prefix(code)}{html.escape(path)}"/>'
        )
    lines.append(
        f'    <xhtml:link rel="alternate" hreflang="x-default" '
        f'href="{SITE_URL}/{html.escape(alt["ar"])}"/>'
    )
    lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append("  </url>")
    return "\n".join(lines)


def build_sitemap(ar_pieces: list, published: dict) -> None:
    today = max((p["date"] for p in ar_pieces), default="2026-01-01")
    entries = []
    for canonical in ("index.html", "book.html"):
        alt = {code: canonical for code in LANG_ORDER}
        entries.append(sitemap_url(canonical, alt, today))
    for piece in ar_pieces:
        canonical = piece_path(piece)
        alt = {}
        for code in LANG_ORDER:
            if code == "ar" or piece["slug"] in published.get(code, set()):
                alt[code] = canonical
        entries.append(sitemap_url(canonical, alt, piece["date"]))
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("بُني: sitemap.xml")


if __name__ == "__main__":
    main()
