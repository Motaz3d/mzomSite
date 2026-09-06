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
  - `content/*.md` — النصوص المنشورة حاليًا على الموقع
  - `queue/*.md` — **طابور النشر المجدول**: نصوص معتمدة تنتظر يومها (بقرار الكاتب 2026-09-06: الاعتماد هنا، والنشر نصًا واحدًا يوميًا بجدول — لا فور الاعتماد)
  - `build.py` — يبني الموقع من `content/` فقط: `python3 build.py` (Python stdlib فقط)
  - `templates/base.html` + `assets/style.css` — القالب والتصميم (ورقي، Amiri/Aref Ruqaa، RTL)
  - `index.html` — **واجهة الكتاب: يعرض أحدث نص كاملًا مباشرة + زر كبير «تصفّح الكتاب»**
  - `book.html` — فهرس الكتاب (كل النصوص بتواريخها)
  - `pieces/*.html` — صفحات النصوص مع أزرار تنقل كبيرة (السابق/الكتاب/التالي)
  - المخرجات مولّدة — لا تُحرَّر يدويًا، أعد البناء
- **Publishing queue:** النشر من الطابور يوميًا بجدولة cron: خ-103 «لي صديق» يوم 2026-09-07 (cron 01M1T2Y2S176GE98YKHD1G8DMS)، خ-150 «علاء» يوم 2026-09-08 (cron 01M1T2Y2S2XYRM7HSNZRJJ1YHJ). عند النشر: `git mv queue/… content/…` + تحديث date + build + push.
- **HTTPS cert:** pending at GitHub (diagnosed 2026-09-06: everything our side correct; retriggered via cname remove/re-add; auto-retry cron 01M1T2JJ28MPZZEKN7QBGE957R every ~40min self-deletes on success).
- **Book being serialized:** «المهاجر — لقطات ومرايا» (الكتاب الأول، خطة `wr/تطوير/خطة-كتاب-المهاجر.md`) — بقرار الكاتب 2026-09-06. قرارات الشكل: النص الأخير على الرئيسية، أزرار كبيرة واضحة، التبحر داخل الكتاب عبر book.html. إيقاع النشر: **طابور مجدول — نص واحد يوميًا** (انظر Publishing queue). الكتب التالية موثقة في `wr/تطوير/الخطة-المتكاملة.md` (رسائل بين، لبن، مقالات) — نبدأ بها بعد انتهاج «المهاجر».
- **Commands:** بعد إضافة/تعديل ملف في `content/`: `python3 build.py && git add -A && git commit && git push`
- **Libraries:** none (plain HTML/CSS, Python stdlib build)
- **Content source:** النصوص من ورشة الكتابة `/Users/digital-inclusion/Documents/work/wr` — يُنشر فقط ما يوافق عليه الكاتب بموافقة نهائية موثقة (درس خ-031). **المنشور الآن:** خ-102 «مشاكسة الموريتانيّة». **في الطابور:** خ-103 «لي صديق» (2026-09-07)، خ-150 «علاء» (2026-09-08). ملاحظة تقنية: ترتيب النصوص يُحسم برقم خ عند تساوي التاريخ.
- **Domain/DNS:** custom domain `motazomarien.com` (CNAME file in repo). Registrar + DNS: **Regery** (الهجرة من Virtono اكتملت 2026-09-05؛ لم يعد لـ Virtono أي صلة بالنطاق). Zone keeps only GitHub A records + www CNAME. Mail: user's personal Gmail — no MX records. User does NOT use Zoho.
