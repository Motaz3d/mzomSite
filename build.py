#!/usr/bin/env python3
"""يبني ملفات الموقع الساكن (جناح الألعاب).

المصدر: صفحات الجذر المكتوبة يدويًا —
    index.html (en), bs.html, fr.html, de.html, ar.html

الناتج:
    sitemap.xml — خريطة الموقع بكل لغات جناح الألعاب (hreflang)

الاستخدام:
    python3 build.py
"""

import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SITE_URL = "https://motazomarien.com"

# جناح الألعاب — الجذر (إنكليزي أساسًا) وبقية اللغات، بترتيب العرض في المبدّل
GAMES_ORDER = ["en", "bs", "fr", "de", "ar"]
GAMES_FILES = {"en": "index.html", "bs": "bs.html", "fr": "fr.html",
               "de": "de.html", "ar": "ar.html"}
DEFAULT_LANG = "en"


def sitemap_url(canonical: str, alt: dict, lastmod: str) -> str:
    lines = [
        "  <url>",
        f"    <loc>{SITE_URL}/{html.escape(canonical)}</loc>",
    ]
    for code, path in alt.items():
        lines.append(
            f'    <xhtml:link rel="alternate" hreflang="{code}" '
            f'href="{SITE_URL}/{html.escape(path)}"/>'
        )
    lines.append(
        f'    <xhtml:link rel="alternate" hreflang="x-default" '
        f'href="{SITE_URL}/{html.escape(alt[DEFAULT_LANG])}"/>'
    )
    lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines.append("  </url>")
    return "\n".join(lines)


def build_sitemap() -> None:
    today = date.today().isoformat()
    games_alt = {code: GAMES_FILES[code] for code in GAMES_ORDER}
    entries = [
        sitemap_url(GAMES_FILES[code], games_alt, today) for code in GAMES_ORDER
    ]
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("بُني: sitemap.xml")


def main() -> None:
    build_sitemap()


if __name__ == "__main__":
    main()
