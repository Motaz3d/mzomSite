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
  - `content/*.md` — النصوص المنشورة حاليًا على الموقع (الأصل العربي)
  - `translations/{en,es,zh}/*.md` — **ترجمات النصوص المنشورة** (إنكليزي/إسباني/صيني)، بنفس تنسيق الترويسة ونفس `slug`. لا تُعرض ترجمة إلا إذا كان أصلها منشورًا في `content/`.
  - `queue/*.md` — **طابور النشر المجدول**: نصوص معتمدة تنتظر يومها (بقرار الكاتب 2026-09-06: الاعتماد هنا، والنشر نصًا واحدًا يوميًا بجدول — لا فور الاعتماد). **الطابور عربي فقط ولا يُترجم قبل النشر.**
  - `build.py` — يبني الموقع من `content/` + `translations/`: `python3 build.py` (Python stdlib فقط). كل اللغات تُبنى معًا دائمًا. يولّد أيضًا `sitemap.xml` و`feed.xml` (RSS عربي لآخر 20 نصًا — لحملة البريد اليومية). **طبقة التفاعل:** زر مشاركة واتساب يظهر دائمًا تحت كل نص؛ نموذج التعليقات (Web3Forms → بريد الكاتب) ونموذج الاشتراك البريدي (Mailchimp) وزر قناة واتساب تظهر فقط بعد لصق قيمها في الثوابت `WEB3FORMS_ACCESS_KEY` / `NEWSLETTER_FORM_ACTION` / `WHATSAPP_CHANNEL_URL` أعلى build.py ثم إعادة البناء.
  - `templates/base.html` + `assets/style.css` — القالب والتصميم (ورقي؛ Amiri/Aref Ruqaa للعربية، EB Garamond للإنكليزية/الإسبانية، Noto Serif SC للصينية؛ RTL للعربية فقط)
  - `assets/brand/` — الهوية البصرية: `logo.png` (الشعار الكامل الشفاف)، `monogram.png` (المونوغرام المربع: أيقونة المتصفح + ترويسة الموقع)، `og.png` (الشعار على خلفية ورقية لمشاركات التواصل og:image)
  - `robots.txt` + `sitemap.xml` — للزحف والفهرسة (sitemap تولّدها build.py بكل اللغات مع hreflang)
  - `index.html` — **واجهة الكتاب: يعرض أحدث نص كاملًا مباشرة + زر كبير «تصفّح الكتاب»**
  - `book.html` — فهرس الكتاب (كل النصوص بتواريخها)
  - `pieces/*.html` — صفحات النصوص مع أزرار تنقل كبيرة (السابق/الكتاب/التالي). سطر الميتا يعرض «لقطة N» (رقم النشر التسلسلي) — **أرقام خ داخلية فقط ولا تظهر في الواجهة** (قرار الكاتب 2026-09-07)
  - `en/ es/ zh/` — نفس البنية مولّدة لكل لغة (index + book + pieces)، مع محوّل لغات في الترويسة ووسوم hreflang
  - المخرجات مولّدة — لا تُحرَّر يدويًا، أعد البناء
- **Publishing queue:** النشر من الطابور نص واحد يوميًا بجدول (النشر يحتاج جلسة وكيل للترجمة — يُطلب بـ«انشر نص اليوم» في أي جلسة): خ-150 «علاء» يوم 2026-09-08، خ-142 «نزار طه حاج أحمد» يوم 2026-09-09، خ-096 «سراب بسراب بسراب» يوم 2026-09-10، خ-091 «طيرة حيفا» يوم 2026-09-11، خ-162 «روحك تموت» يوم 2026-09-12 (سلسلة جديدة: «يوميات المهاجر»). عند النشر: `git mv queue/… content/…` + تحديث date + **إضافة ترجماته الثلاث إلى `translations/{en,es,zh}/<slug>.md` بجودة أدبية عالية** + build + push. (نص بلا ترجمات يظهر عربيًا فقط حتى تُضاف.)
- **HTTPS cert:** pending at GitHub (diagnosed 2026-09-06: everything our side correct; DNS verified). Watcher: **launchd agent `com.motazomarien.httpscheck`** (`~/scripts/https-cert-check/check.sh`, every 30min, retrigger throttled to once/6h; on success enables Enforce HTTPS + self-deletes) — يعمل بلا أي جلسة Kimi مفتوحة (يتطلب أن يكون الماك مستيقظًا).
- **Book being serialized:** «المهاجر — لقطات ومرايا» (الكتاب الأول، خطة `wr/تطوير/خطة-كتاب-المهاجر.md`) — بقرار الكاتب 2026-09-06. قرارات الشكل: النص الأخير على الرئيسية، أزرار كبيرة واضحة، التبحر داخل الكتاب عبر book.html. إيقاع النشر: **طابور مجدول — نص واحد يوميًا** (انظر Publishing queue). الكتب التالية موثقة في `wr/تطوير/الخطة-المتكاملة.md` (رسائل بين، لبن، مقالات) — نبدأ بها بعد انتهاج «المهاجر».
- **Commands:** بعد إضافة/تعديل ملف في `content/`: `python3 build.py && git add -A && git commit && git push`
- **Libraries:** none (plain HTML/CSS, Python stdlib build)
- **Content source:** النصوص من ورشة الكتابة `/Users/digital-inclusion/Documents/work/wr` — يُنشر فقط ما يوافق عليه الكاتب بموافقة نهائية موثقة (درس خ-031). **المنشور الآن:** خ-103 «لي صديق» (2026-09-07، بترجماته الثلاث). **في الطابور:** خ-150 «علاء» (09-08)، خ-142 «نزار طه» (09-09)، خ-096 «سراب» (09-10)، خ-091 «طيرة حيفا» (09-11)، خ-162 «روحك تموت» (09-12 — سلسلة «يوميات المهاجر»). ملاحظة تقنية: ترتيب النصوص يُحسم برقم خ عند تساوي التاريخ.
- **Domain/DNS:** custom domain `motazomarien.com` (CNAME file in repo). Registrar + DNS: **Regery** (الهجرة من Virtono اكتملت 2026-09-05؛ لم يعد لـ Virtono أي صلة بالنطاق). Zone keeps only GitHub A records + www CNAME. Mail: user's personal Gmail — no MX records. User does NOT use Zoho.
