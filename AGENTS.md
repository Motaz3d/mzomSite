# AGENTS.md — mzomSite

## قاعدة ملزمة: الاستشارة ≠ التنفيذ (توجيه الكاتب 2026-09-21)

- ما يطلبه الكاتب **استشارةً** يبقى استشارة: لا تعديل ملفات، لا `python3 build.py`، لا `git commit`، ولا `git push` إلا بطلب تنفيذ صريح («نفّذ»، «ابنِ»، «احفظ»، «انشر»…).
- الاستشارة تعني: تحليل وخطة ونصوص مقترحة تُعرض في الجلسة فقط — والتنفيذ يبدأ بعد موافقة صريحة.
- خلفية: في 2026-09-21 طلب الكاتب استشارة عن توحيد خدماته فنفّذ الوكيل «طبقة الخدمات» كاملة والتزم بها محليًا دون طلب (الالتزام 81d4e39 محلي، غير مدفوع — يُبقى أو يُلغى بقرار الكاتب).

## Session protocol (automatic)

1. **At the start of every session:** read `PLAN.md` first to know the current state of work. Do not re-inspect or re-verify work that is already marked as done.
2. **While working:** use this map (project structure below) instead of random searching.
3. **Before finishing any task:** update automatically, without being asked:
   - `AGENTS.md` — if the structure/architecture changed.
   - `PLAN.md` — if the work status changed.

## Project map

- **Type:** static website hosted on **GitHub Pages** (repo: Motaz3d/mzomSite, branch `main`, path `/`)
- **Live URL:** **https://motazomarien.com** (HTTPS فعّال منذ 2026-09-08 — شهادة Let's Encrypt صدرت وEnforce HTTPS مفعّل)
- **Repo visibility:** **public** (required for Pages on the free plan)
- **⚠️ تحوّل الموقع (2026-09-27 — قرار الكاتب):** **أُزيل جناح الكتابة نهائيًا** (الخيار «ج»: حذف كامل مع الاحتفاظ بنسخة محلية). الموقع الآن **جناح ألعاب + صفحة خدمات** فقط. النسخة المحلية الكاملة للكتابة: `~/Documents/work/mzomsite-writing-archive-2026-09-27/`.
- **Structure (الحال بعد الإزالة):**
  - `index.html` (إنكليزي، الجذر) + `bs.html` + `fr.html` + `de.html` + `ar.html` — **صفحات جناح الألعاب الخمس، مكتوبة يدويًا** (لا يبنيها `build.py`): عرض لعبتين خشبيتين (صندوق الرمل، أحرف الفاتحة)، سعر **٢٥ يورو** للعبة (نمط `.price`)، الطلب عبر البريد `motazomarien@gmail.com`، وإصدار **فاتورة رسمية** مع كل طلب — مناسبة للشركات. الأنماط في `assets/games.css`.
  - `web.html` — **صفحة الخدمات** (إنكليزية، الجذر): إنشاء المواقع والتطبيقات — Hero + «ما أبنيه» (٦ خدمات) + «أعمال مختارة» (Talaix · Talaiz · هذا الموقع) + «كيف أعمل» + «القدرات التقنية» + بريد التواصل. **مكتوبة يدويًا**، `noindex`، وغير مُدرجة في `sitemap.xml`. يدخلها زرّ `Build your site` (نمط `.svc-link`) في ترويسات الصفحات الخمس.
  - `build.py` — **مولّد `sitemap.xml` فقط** (~٧٠ سطرًا، Python stdlib): ٥ مسارات (صفحات الألعاب) مع hreflang و`x-default` → `index.html`. الاستخدام: `python3 build.py`.
  - `404.html` — صفحة «غير موجود» + تحويل مسارات الكتابة القديمة (`/writing/…`، `/book.html`، `/pieces/…`، `/series/…`، `/{en,es,zh,ru,pt,de}/…`) إلى `/`.
  - `assets/brand/` — الهوية البصرية: `logo.png`، `monogram.png` (أيقونة المتصفح + ترويسة الموقع)، `og.png` (og:image).
  - `robots.txt` + `sitemap.xml` — للزحف والفهرسة. `CNAME` — النطاق المخصّص.
  - **`noindex` على كل صفحات الموقع حاليًا:** الموقع غير مفهرس، وصفحات الألعاب تسمّي نفسها «نموذجًا أوليًا» في التذييل وقسم `.note`. تُفهرس بإزالة وسم `noindex` والنصوص المذكورة عند طلب الكاتب.
  - **النشر على Pages:** legacy **«Deploy from a branch»** (main، /root) — كل push يُشغّل بناء تلقائيًا. درس 2026-09-09: المصدر انقلب بصمت إلى «GitHub Actions» فتوقفت الدفعات يومًا كاملًا وظهرت 404؛ أعاد الكاتب المصدر إلى branch من إعدادات المستودع (Settings ← Pages) وعاد البناء فورًا. إن توقفت الدفعات مجددًا افحص هذا الإعداد أولًا.
- **ما أُزيل نهائيًا (2026-09-27):** `content/`، `translations/{en,es,zh,ru,pt,de}/`، `queue/`، `writing/`، `templates/base.html`، `assets/style.css`، `feed.xml` — ومعها: الكتاب المتسلسل «المهاجر — لقطات ومرايا»، طابور النشر اليومي، مشروع التشكيل، الترجمات السبع، صفحات السلاسل والقطع، صفحة `thanks.html`، وطبقة التفاعل كلها (تعليقات Web3Forms، اشتراك Mailchimp، مشاركة واتساب و«انسخ الرابط»، قناة واتساب، قناة يوتيوب).
- **HTTPS:** **resolved 2026-09-08** — Let's Encrypt cert active (apex+www), Enforce HTTPS on, watcher self-deleted. Details in PLAN.md.
- **Commands:** بعد تعديل أي صفحة: `python3 build.py && git add -A && git commit && git push`. (لا يوجد محتوى Markdown بعد الآن — الصفحات تُحرَّر يدويًا.)
- **Libraries:** none (plain HTML/CSS, Python stdlib build)
- **الطلب والدفع:** الطلب **بالبريد فقط** من الصفحات الخمس. **لا بوابة دفع على الموقع** (الموقع ساكن على GitHub Pages، ولا خادم). **Stripe** قيد التجهيز عند الكاتب (test mode) لغرض **إصدار الفواتير** للشركات — لا للدفع على الموقع. السعر المعروض: **٢٥ يورو** للعبة.
- **Domain/DNS:** custom domain `motazomarien.com` (CNAME file in repo). Registrar + DNS: **Regery** (الهجرة من Virtono اكتملت 2026-09-05؛ لم يعد لـ Virtono أي صلة بالنطاق). Zone keeps GitHub A records + www CNAME + google-site-verification TXT + **ImprovMX mail records (أُضيفت 2026-09-09): MX @ ← mx1.improvmx.com (10) وmx2.improvmx.com (20)، TXT @ ← `v=spf1 include:spf.improvmx.com ~all`** + **DKIM لـ Mailchimp (أُضيفا 2026-09-09): CNAME k1._domainkey وk2._domainkey ← dkim.mcsv.net** + **DMARC (أُضيف 2026-09-14): TXT `_dmarc` ← `v=DMARC1; p=none`**. Mail: **`motaz@motazomarien.com` يُحوَّل عبر ImprovMX (مجاني) إلى Gmail الشخصي motaz3d@gmail.com** — استقبال فقط. **درس 2026-09-14:** يجب وجود alias صريح `motaz` ← `motaz3d@gmail.com`؛ الـ catch-all وحده إذا وُجّه إلى عنوان على النطاق نفسه يُنشئ حلقة تُسقط البريد. User does NOT use Zoho. **ملاحظة (2026-09-27):** سجلات Mailchimp/DKIM باقية في الـ DNS لكن **Mailchimp لم يعد مستخدمًا** — أُزيلت النشرة مع جناح الكتابة.
