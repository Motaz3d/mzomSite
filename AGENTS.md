# AGENTS.md — mzomSite

## Session protocol (automatic)

1. **At the start of every session:** read `PLAN.md` first to know the current state of work. Do not re-inspect or re-verify work that is already marked as done.
2. **While working:** use this map (project structure below) instead of random searching.
3. **Before finishing any task:** update automatically, without being asked:
   - `AGENTS.md` — if the structure/architecture changed.
   - `PLAN.md` — if the work status changed.

## Project map

- **Type:** static website hosted on **GitHub Pages** (repo: Motaz3d/mzomSite, branch `main`, path `/`)
- **Live URL:** https://motaz3d.github.io/mzomSite/ — **working (status: built)** (custom domain pending — see PLAN.md)
- **Repo visibility:** **public** (required for Pages on the free plan)
- **Structure:**
  - `content/*.md` — النصوص المنشورة (ترويسة: title/series/number/kh/slug/date ثم النص)
  - `build.py` — يحوّل `content/` إلى HTML: `python3 build.py` (Python stdlib فقط)
  - `templates/base.html` + `assets/style.css` — القالب والتصميم (ورقي، Amiri/Aref Ruqaa، RTL)
  - `pieces/*.html` + `index.html` — مخرجات مولّدة (لا تُحرَّر يدويًا، أعد البناء)
- **Commands:** بعد إضافة/تعديل ملف في `content/`: `python3 build.py && git add -A && git commit && git push`
- **Libraries:** none (plain HTML/CSS, Python stdlib build)
- **Content source:** النصوص من ورشة الكتابة `/Users/digital-inclusion/Documents/work/wr` — يُنشر فقط ما يوافق عليه الكاتب، وحاليًا مسار **الاغتراب** فقط (رواية بلا عنوان، تفتتحها سلسلة «رسائل إلى مارينا»). المنشور حتى الآن: خ-031 (pieces/marina-1-lissan.html).
- **Domain/DNS:** custom domain `motazomarien.com` (CNAME file in repo). Registrar: Regery. Currently on Virtono nameservers — **user is migrating to Regery NS to leave Virtono entirely** (see PLAN.md exit plan). After the NS switch, Regery's DNS zone becomes active (GitHub A records + www CNAME already entered there). Mail: user's personal Gmail — no MX records needed. User does NOT use Zoho.
