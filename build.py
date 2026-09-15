#!/usr/bin/env python3
"""يبني الموقع بعدّة لغات.

المصدر:
    content/*.md               — النصوص العربية المنشورة (الأصل)
    translations/<lang>/*.md   — ترجماتها (en, es, zh, ru, pt, de) بنفس تنسيق الترويسة ونفس slug.
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
WEB3FORMS_ACCESS_KEY = "84872369-05da-4ba4-a629-c426879bb250"    # تعليقات القراء → بريد الكاتب — المفتاح من web3forms.com (تدخل بريدك فيصلك المفتاح فورًا)
NEWSLETTER_FORM_ACTION = "https://motazomarien.us2.list-manage.com/subscribe/post?u=8837b8070f6417c372512ba8c&id=69d8847d9d"  # نموذج الاشتراك البريدي — رابط النموذج المضمّن من Mailchimp (Audience → Signup forms → Embedded forms)
WHATSAPP_CHANNEL_URL = ""    # رابط قناة واتساب — تُنشأ من تطبيق واتساب (التحديثات ← القنوات ← إنشاء قناة)

LANG_ORDER = ["ar", "en", "es", "zh", "ru", "pt", "de"]

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
    "ru": {
        "dir": "ltr",
        "label": "Русский",
        "site_name": "Мотаз Омарин",
        "tagline": "Роман без названия — об отчуждении",
        "book_title": "Мигрант — кадры и зеркала",
        "book_intro": (
            "Очень короткие рассказы, дающие голос боли — от еврейского "
            "квартала в Дамаске до кафе Люксембурга. Книга появляется здесь "
            "кадр за кадром, новый текст каждый день."
        ),
        "footer": "motazomarien.com — публикуется с продолжением, каждый день новая история",
        "prev": "← Предыдущий текст",
        "book_full": "Вся книга",
        "next": "Следующий текст →",
        "browse": "Полистать всю книгу →",
        "piece_word": "Кадр",
        "index_desc": "Книга «{book}» — публикуется кадр за кадром на сайте {name}",
        "book_desc": "Указатель опубликованных на сегодня текстов из книги «{book}»",
        "piece_desc": "{title} — из книги «{book}»",
        "book_page_title": "Вся книга — {book}",
        "empty_index": "Первый текст скоро появится — он будет опубликован здесь целиком в день выхода, раньше, чем где-либо ещё.",
        "empty_book": "Текстов пока нет — первый кадр уже в пути.",
        "share_wa": "Поделиться текстом в WhatsApp",
        "comment_title": "Ваш комментарий дойдёт до автора",
        "comment_note": "Оставьте имя, электронную почту и комментарий — он попадёт прямо в почту автора и не будет опубликован.",
        "comment_name": "Имя",
        "comment_email": "Электронная почта",
        "comment_msg": "Ваш комментарий…",
        "comment_send": "Отправить",
        "comment_subject": "Комментарий к: {title}",
        "news_title": "Получайте текст дня",
        "news_note": "Подпишитесь, чтобы получать каждый новый текст в день публикации, или следите за каналом в WhatsApp.",
        "news_button": "Подписаться",
        "news_email": "Ваша электронная почта",
        "wa_channel": "Следить за каналом в WhatsApp →",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">'
        ),
    },
    "pt": {
        "dir": "ltr",
        "label": "Português",
        "site_name": "Motaz Omarien",
        "tagline": "Um romance sem título — sobre a alienação",
        "book_title": "O Migrante — Instantâneos e Espelhos",
        "book_intro": (
            "Relatos muito breves que dão voz à dor — do bairro judeu de "
            "Damasco aos cafés do Luxemburgo. O livro publica-se aqui "
            "instantâneo a instantâneo, um texto novo a cada dia."
        ),
        "footer": "motazomarien.com — publicado em série, uma história por dia",
        "prev": "← Texto anterior",
        "book_full": "O livro completo",
        "next": "Texto seguinte →",
        "browse": "Explorar o livro completo →",
        "piece_word": "Instantâneo",
        "index_desc": "O livro «{book}» — publicado instantâneo a instantâneo no site de {name}",
        "book_desc": "Índice dos textos publicados até agora de «{book}»",
        "piece_desc": "{title} — do livro «{book}»",
        "book_page_title": "O livro completo — {book}",
        "empty_index": "O primeiro texto chegará em breve — aparecerá aqui na íntegra no momento em que for publicado, antes de qualquer outro lugar.",
        "empty_book": "Ainda não há textos publicados — o primeiro instantâneo está a caminho.",
        "share_wa": "Partilhar este texto no WhatsApp",
        "comment_title": "O teu comentário chega ao autor",
        "comment_note": "Deixa o teu nome, e-mail e comentário — chega diretamente à caixa de entrada do autor; nada é publicado publicamente.",
        "comment_name": "Nome",
        "comment_email": "E-mail",
        "comment_msg": "O teu comentário…",
        "comment_send": "Enviar",
        "comment_subject": "Comentário sobre: {title}",
        "news_title": "Recebe o texto do dia",
        "news_note": "Subscreve com o teu e-mail para receberes cada texto novo no dia da publicação, ou segue o canal do WhatsApp.",
        "news_button": "Subscrever",
        "news_email": "O teu e-mail",
        "wa_channel": "Seguir o canal do WhatsApp →",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
        ),
    },
    "de": {
        "dir": "ltr",
        "label": "Deutsch",
        "site_name": "Motaz Omarien",
        "tagline": "Ein Roman ohne Titel — über die Entfremdung",
        "book_title": "Der Migrant — Momentaufnahmen und Spiegel",
        "book_intro": (
            "Sehr kurze Geschichten, die dem Schmerz eine Stimme geben — vom jüdischen "
            "Viertel in Damaskus bis zu den Cafés von Luxemburg. Das Buch erscheint hier "
            "Momentaufnahme für Momentaufnahme, jeden Tag ein neuer Text."
        ),
        "footer": "motazomarien.com — in Fortsetzungen veröffentlicht, jeden Tag eine Geschichte",
        "prev": "← Vorheriger Text",
        "book_full": "Das ganze Buch",
        "next": "Nächster Text →",
        "browse": "Das ganze Buch durchblättern →",
        "piece_word": "Momentaufnahme",
        "index_desc": "Das Buch „{book}“ — Momentaufnahme für Momentaufnahme auf der Seite von {name}",
        "book_desc": "Verzeichnis der bisher veröffentlichten Texte aus „{book}“",
        "piece_desc": "{title} — aus dem Buch „{book}“",
        "book_page_title": "Das ganze Buch — {book}",
        "empty_index": "Der erste Text erscheint bald — er wird hier vollständig zu sehen sein, sobald er veröffentlicht wird, früher als überall sonst.",
        "empty_book": "Noch keine Texte veröffentlicht — die erste Momentaufnahme ist unterwegs.",
        "share_wa": "Diesen Text über WhatsApp teilen",
        "comment_title": "Dein Kommentar erreicht den Autor",
        "comment_note": "Hinterlasse deinen Namen, deine E-Mail und deinen Kommentar — er geht direkt in das Postfach des Autors und wird nicht öffentlich veröffentlicht.",
        "comment_name": "Name",
        "comment_email": "E-Mail",
        "comment_msg": "Dein Kommentar…",
        "comment_send": "Senden",
        "comment_subject": "Kommentar zu: {title}",
        "news_title": "Erhalte den Text des Tages",
        "news_note": "Abonniere mit deiner E-Mail, um jeden neuen Text am Tag seines Erscheinens zu erhalten, oder folge dem WhatsApp-Kanal.",
        "news_button": "Abonnieren",
        "news_email": "Deine E-Mail",
        "wa_channel": "Dem WhatsApp-Kanal folgen →",
        "fonts": (
            '<link href="https://fonts.googleapis.com/css2?'
            'family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
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
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня",
           "июля", "августа", "сентября", "октября", "ноября", "декабря"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
           "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni",
           "Juli", "August", "September", "Oktober", "November", "Dezember"],
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


# ─── نصوص الطبقة التفاعلية: تأكيد الاشتراك داخل الصفحة، نسخ الرابط، صفحة الشكر ───
EXTRA_STRINGS = {
    "ar": {
        "subscribe_thanks": "شكرًا لك — وصل اشتراكك بنجاح.",
        "copy_link": "انسخ الرابط",
        "copied": "تم النسخ ✓",
        "thanks_title": "شكرًا لك",
        "thanks_body": "وصلت رسالتك، وسأقرأها باهتمام.",
        "thanks_back": "عودة إلى الموقع",
    },
    "en": {
        "subscribe_thanks": "Thank you — your subscription was received.",
        "copy_link": "Copy link",
        "copied": "Copied ✓",
        "thanks_title": "Thank you",
        "thanks_body": "Your message has arrived, and I'll read it with care.",
        "thanks_back": "Back to the site",
    },
    "es": {
        "subscribe_thanks": "Gracias — tu suscripción se ha recibido.",
        "copy_link": "Copiar enlace",
        "copied": "Copiado ✓",
        "thanks_title": "Gracias",
        "thanks_body": "Tu mensaje ha llegado y lo leeré con atención.",
        "thanks_back": "Volver al sitio",
    },
    "zh": {
        "subscribe_thanks": "谢谢你——订阅已收到。",
        "copy_link": "复制链接",
        "copied": "已复制 ✓",
        "thanks_title": "谢谢你",
        "thanks_body": "你的留言已经收到，我会用心阅读。",
        "thanks_back": "返回网站",
    },
    "ru": {
        "subscribe_thanks": "Спасибо — ваша подписка получена.",
        "copy_link": "Скопировать ссылку",
        "copied": "Скопировано ✓",
        "thanks_title": "Спасибо",
        "thanks_body": "Ваше сообщение получено, я прочту его с вниманием.",
        "thanks_back": "Вернуться на сайт",
    },
    "pt": {
        "subscribe_thanks": "Obrigado — a tua subscrição foi recebida.",
        "copy_link": "Copiar ligação",
        "copied": "Copiado ✓",
        "thanks_title": "Obrigado",
        "thanks_body": "A tua mensagem chegou e vou lê-la com atenção.",
        "thanks_back": "Voltar ao site",
    },
    "de": {
        "subscribe_thanks": "Danke — deine Anmeldung ist eingegangen.",
        "copy_link": "Link kopieren",
        "copied": "Kopiert ✓",
        "thanks_title": "Danke",
        "thanks_body": "Deine Nachricht ist angekommen, und ich werde sie mit Aufmerksamkeit lesen.",
        "thanks_back": "Zurück zur Seite",
    },
}
for _code, _extra in EXTRA_STRINGS.items():
    LANGS[_code].update(_extra)


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
            out.append(f"<p>{md_inline(block).replace(chr(10), '<br>')}</p>")
    return "\n".join(out)


def fmt_date(lang: str, iso: str) -> str:
    year, month, day = (int(part) for part in iso.split("-"))
    if lang == "ar":
        return f"{day} {MONTHS['ar'][month - 1]} {year}"
    if lang == "en":
        return f"{MONTHS['en'][month - 1]} {day}, {year}"
    if lang == "es":
        return f"{day} de {MONTHS['es'][month - 1]} de {year}"
    if lang == "ru":
        return f"{day} {MONTHS['ru'][month - 1]} {year}"
    if lang == "pt":
        return f"{day} de {MONTHS['pt'][month - 1]} de {year}"
    if lang == "de":
        return f"{day}. {MONTHS['de'][month - 1]} {year}"
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


def piece_url(lang: str, piece: dict) -> str:
    return f"{SITE_URL}/{lang_prefix(lang)}{piece_path(piece)}"


def share_url(lang: str, piece: dict) -> str:
    return f"https://wa.me/?text={quote(piece['title'] + ' — ' + piece_url(lang, piece))}"


def interact_section(lang: str, piece: dict) -> str:
    strings = LANGS[lang]
    parts = ['<section class="interact">']
    parts.append(
        '<p class="center">'
        f'<a class="big-button secondary" href="{share_url(lang, piece)}" '
        f'target="_blank" rel="noopener">{strings["share_wa"]}</a>'
        f'<button type="button" class="big-button secondary copy-link" hidden '
        f'data-url="{html.escape(piece_url(lang, piece))}" '
        f'data-label="{html.escape(strings["copy_link"])}" '
        f'data-copied="{html.escape(strings["copied"])}">{strings["copy_link"]}</button>'
        '</p>'
    )
    if WEB3FORMS_ACCESS_KEY:
        subject = strings["comment_subject"].format(title=piece["title"])
        parts.append(
            f'<h2 class="interact-title">{strings["comment_title"]}</h2>\n'
            f'<p class="interact-note">{strings["comment_note"]}</p>\n'
            '<form class="comment-form" action="https://api.web3forms.com/submit" method="POST">\n'
            f'  <input type="hidden" name="access_key" value="{WEB3FORMS_ACCESS_KEY}">\n'
            f'  <input type="hidden" name="subject" value="{html.escape(subject)}">\n'
            f'  <input type="hidden" name="redirect" value="{SITE_URL}/{lang_prefix(lang)}thanks.html">\n'
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
            f'<form class="subscribe-form" id="subscribe-form" action="{NEWSLETTER_FORM_ACTION}" '
            'method="post" target="_blank">\n'
            f'  <input type="email" name="EMAIL" placeholder="{strings["news_email"]}" required>\n'
            f'  <button type="submit" class="big-button">{strings["news_button"]}</button>\n'
            '</form>\n'
            f'<iframe name="mc_frame" title="{strings["news_title"]}" style="display:none"></iframe>\n'
            f'<p class="form-thanks" id="subscribe-thanks" hidden>{strings["subscribe_thanks"]}</p>'
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

    thanks_content = (
        '<section class="hero">'
        f'<h1 class="book-title">{strings["thanks_title"]}</h1>'
        f'<p class="intro">{strings["thanks_body"]}</p>'
        f'<p class="center"><a class="big-button" href="index.html">{strings["thanks_back"]}</a></p>'
        "</section>"
    )
    thanks = render(
        lang,
        title=strings["thanks_title"],
        description=strings["thanks_body"],
        content_html=thanks_content,
        root=root,
        home="index.html",
        alt=alt_for("thanks.html"),
    )
    (out_root / "thanks.html").write_text(thanks, encoding="utf-8")
    print(f"بُني: {lang_prefix(lang)}thanks.html")


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
