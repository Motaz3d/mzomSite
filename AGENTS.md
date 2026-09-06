# AGENTS.md — mzomSite

## Session protocol (automatic)

1. **At the start of every session:** read `PLAN.md` first to know the current state of work. Do not re-inspect or re-verify work that is already marked as done.
2. **While working:** use this map (project structure below) instead of random searching.
3. **Before finishing any task:** update automatically, without being asked:
   - `AGENTS.md` — if the structure/architecture changed.
   - `PLAN.md` — if the work status changed.

## Project map

- **Type:** static website hosted on **GitHub Pages** (repo: Motaz3d/mzomSite, branch `main`, path `/`)
- **Live URL:** **http://motazomarien.com** (يعمل؛ HTTPS قيد إصدار الشهادة — يُفعَّل تلقائيًا، انظر PLAN.md)
- **Repo visibility:** **public** (required for Pages on the free plan)
- **Structure:**
  - `content/*.md` — النصوص المنشورة (ترويسة: title/series/number/kh/slug/date ثم النص)
  - `build.py` — يحوّل `content/` إلى HTML: `python3 build.py` (Python stdlib فقط)
  - `templates/base.html` + `assets/style.css` — القالب والتصميم (ورقي، Amiri/Aref Ruqaa، RTL)
  - `index.html` — **واجهة الكتاب: يعرض أحدث نص كاملًا مباشرة + زر كبير «تصفّح الكتاب»**
  - `book.html` — فهرس الكتاب (كل النصوص بتواريخها)
  - `pieces/*.html` — صفحات النصوص مع أزرار تنقل كبيرة (السابق/الكتاب/التالي)
  - المخرجات مولّدة — لا تُحرَّر يدويًا، أعد البناء
- **Book being serialized:** «المهاجر — لقطات ومرايا» (الكتاب الأول، خطة `wr/تطوير/خطة-كتاب-المهاجر.md`) — بقرار الكاتب 2026-09-06. قرارات الشكل: النص الأخير على الرئيسية، أزرار كبيرة واضحة، التبحر داخل الكتاب عبر book.html. إيقاع النشر: مخزون 7 نصوص معتمدة أولًا، ثم نشر يومي. الكتب التالية موثقة في `wr/تطوير/الخطة-المتكاملة.md` (رسائل بين، لبن، مقالات) — نبدأ بها بعد انتهاج «المهاجر».
- **Commands:** بعد إضافة/تعديل ملف في `content/`: `python3 build.py && git add -A && git commit && git push`
- **Libraries:** none (plain HTML/CSS, Python stdlib build)
- **Content source:** النصوص من ورشة الكتابة `/Users/digital-inclusion/Documents/work/wr` — يُنشر فقط ما يوافق عليه الكاتب، وحاليًا مسار **الاغتراب** فقط (رواية بلا عنوان، تفتتحها سلسلة «رسائل إلى مارينا»). **لا منشور حاليًا:** خ-031 نُشرت ثم حذفها الكاتب (2026-09-05) — غير راضٍ عنها. `build.py` يتعامل مع موقع بلا نصوص (رسالة «قريبًا»).
- **Domain/DNS:** custom domain `motazomarien.com` (CNAME file in repo). Registrar + DNS: **Regery** (الهجرة من Virtono اكتملت 2026-09-05؛ لم يعد لـ Virtono أي صلة بالنطاق). Zone keeps only GitHub A records + www CNAME. Mail: user's personal Gmail — no MX records. User does NOT use Zoho.
