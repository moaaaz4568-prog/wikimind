# DESIGN — تصميم wikimind

> كل ادعاء واقعي موسوم: `OBSERVED` / `REPORTED` / `PROPOSED` / `UNKNOWN` /
> `NOT_RUN` (انظر README.md للقاعدة). التصميم هنا هو ما **نُفّذ فعلاً** في
> `src/wikimind/` زائد القرارات الملزمة، لا أمنيات.

## 1. المبدأ

نظام عام صغير يعمل محلياً بأقل اعتماديات: الكلمات أولاً، والكثيف اختياري
مقيس لاحقاً — لا خدمة سحابية مدفوعة ولا مفاتيح إطلاقاً [PROPOSED —
phase2-research.md §4.1]. القياس هو البوابة الوحيدة؛ لا بوابات G0–G8 ولا
حوكمة ولا حجر صحي [PROPOSED — قرار ملزم].

## 2. الطبقات

| الطبقة | ماذا | الحالة |
|---|---|---|
| 0. خام | ملفات المستخدم كما هي في مجلداتها (قراءة فقط، لا نقل) | [OBSERVED — يعمل] |
| 1. جرد | `ingest.py` → `manifest.jsonl` + `skipped.jsonl` | [OBSERVED — يعمل] |
| 2. مصطلحات | `terms.py` → `terms.json` + `terms.md` (TF-IDF يدوي + عناوين H1/H2) | [OBSERVED — يعمل] |
| 3. ماسترز | `masters.py` → ماستر مضغوط لكل دومين (سكيل `docs/skills/make-master/`) | [OBSERVED — يعمل: 4 ماسترز على العينة] |
| 4. تقطيع | `chunk.py` → `chunks.jsonl` | [OBSERVED — يعمل] |
| 5. فهرس | `index.py` → `index.json` (BM25 بايثون خالص) | [OBSERVED — يعمل] |
| 6. سؤال | `ask.py` → مقاطع خام مستشهدة | [OBSERVED — يعمل] |
| 7. تقييم | `eval.py` → Recall@k + فحص الاستشهاد على أسئلة معروفة | [OBSERVED — يعمل: n=20، rank-1=0.700] |

الترتيب المنطقي للبناء: ingest → terms/masters (مادة) → chunk → index →
ask → eval. و`terms` مستقل عن `chunk` (يقرأ الخام مباشرة من الـ manifest)
[OBSERVED — `terms.py` يقرأ `abs_path` من `manifest.jsonl`].

## 3. خط الأنابيب

```
corpus/                  -- مجلد المستخدم، أي دومين، أي لغة (.md/.txt)
  └─ ingest --corpus DIR --data DIR
       ├─ manifest.jsonl  {raw_path, abs_path, sha256, sha256_short,
       │                  size_bytes, words, persona}
       └─ skipped.jsonl   {raw_path, reason} لكل مرفوض
  └─ terms --data DIR [--top-n 15]
       ├─ terms.json  {per_doc, global, concepts}
       └─ terms.md    نفس المحتوى مقروءاً للإنسان
  └─ masters --data DIR                              (OBSERVED — يعمل:
       4 ماسترز على العينة، links_verified=40 links_dropped=0)
       └─ <data>/masters/*.md
  └─ chunk --data DIR [--max-words 800]
       └─ chunks.jsonl  {chunk_id, persona, domain, raw_path,
                         sha256_short, section, type, offset,
                         words, bytes, source_lines, text}
  └─ index --data DIR
       └─ index.json  {params{k1,b,...}, N, avgdl, doc_len,
                       idf, postings}
  └─ ask "Q" --data DIR [--top-k 5] [--persona NAME]
              [--min-score 0.0] [--both-sides] [--json]
  └─ eval --data DIR --questions FILE [--out FILE]   (OBSERVED — يعمل:
       n=20 rank-1=0.700 top-3=0.750 على العينة)
```

الأمر الموحّد `python3 -m wikimind <command>` يفوّض كل خطوة لـ `main(argv)`
الخاصة بوحدتها [OBSERVED — `src/wikimind/cli.py`]؛ و`build` يشغّل
ingest→chunk→index→terms→masters بالتسلسل ويتوقف عند أول فشل [OBSERVED —
قُيس كاملاً بنجاح على العينة 2026-11-12].

## 4. الجرد (ingest)

- المقبول: `.md` و`.txt` فقط [OBSERVED — `ingest.py: ACCEPTED_EXTS`].
- Dedupe بمحتوى sha256: المحتوى المكرر يُسجَّل مرة واحدة، والنسخة اللاحقة
  تُستبعد كـ `duplicate_content` [OBSERVED].
- مستبعد ومسجَّل: ملف < 100 بايت، أو ملف محتواه كله 1–2 مسارات نظام خام
  (`/root/...` ونحوها) كـ `pointer_or_too_small` [OBSERVED].
- **محظور قراءته أبداً**: أي مكوّن مسار `07_control` أو `control`، أي مجلد
  مخفي (`.`), `__pycache__`، وأي اسم ملف شكله سر/اعتماد (`*secret*`،
  `*credential*`، `*token*`، `*.pem`، `*.key`، `*.p12`، `id_rsa*`) —
  يُستبعد كـ `excluded_control_or_secret` دون قراءة [OBSERVED].
- Persona صريحة فقط: ملفات تحت `personas/<name>/` في جذر الـ corpus تأخذ
  persona `<name>`؛ كل ما عداها `default`. بلا مجلد `personas/` لا تُفرض
  أي persona [OBSERVED — `ingest.py: persona_for`].
- الخام للقراءة فقط: ingest لا يكتب في الـ corpus أبداً [OBSERVED].

## 5. المصطلحات (terms)

- TF-IDF يدوي: `idf = log(1 + (N-df+0.5)/(df+0.5))` — نفس صيغة idf في BM25
  [OBSERVED — `terms.py`]. أعلى N مصطلحاً لكل وثيقة + ترتيب عام بأفضل score
  للوثيقة [OBSERVED].
- المفاهيم: عناوين H1/H2 لكل وثيقة كما كتبها المؤلف، مع مسارها [OBSERVED].
- لا مكتبة خارجية: `rank-bm25` و`yake` غير مثبّتة في هذه البيئة [OBSERVED —
  phase2-research.md §0]؛ TF-IDF اليدوي هو البديل صفر-الاعتماد الموصى به
  [PROPOSED].
- قيد: جودة TF-IDF على العربية (توكنايزر/تجذير) لم تُقاس هنا [NOT_RUN].

## 6. التقطيع (chunk)

سياسة التقطيع الموروثة (R-2) [REPORTED — phase2-research.md §1]:

- عنوان (`#`…`######`) يبدأ قسماً جديداً؛ ومسار العناوين (عنوان الملف ›
  عنوان القسم) يسافر مع كل مقطع، فيطابق سؤال عنوان القسم حرفياً [OBSERVED].
- داخل القسم: فقرة / جدول (أسطر `|` متتالية) / قائمة (أسطر `-`/`*`/`+`/
  `1.` متتالية). الجدول أو القائمة **وحدة واحدة** لا تُفكَّك إلا إن تجاوزت
  وحدها حد الكلمات [OBSERVED].
- تجميع الكتل في مقطع حتى ~800 كلمة (افتراضي موثق، انظر THRESHOLDS.md)؛
  والكتلة الأطول تُقسَّم على حدود الجمل (`. ! ؟`) لا بالحروف أبداً
  [OBSERVED].
- بلا overlap في v0.1 (افتراضي موثق) [OBSERVED].
- frontmatter في أعلى الملف تُقرأ منها `title`/`concept_id` وتُحذف من نص
  المقاطع [OBSERVED].
- حالة خاصة: الأقسام المضغوطة سطراً واحداً بصيغة `**§N:** ## § N: ...`
  (كما في `NEXUS_BRAIN.md`) تُفكّ: عنوان § يصير عنوان `##` حقيقياً والباقي
  نصاً [OBSERVED — `chunk.py: expand_compressed_lines`].
- metadata كل مقطع: `chunk_id` (من `sha256_short` + تسلسل)، `persona`،
  `domain` (مستنتج من اسم الملف/المسار، وإلا `general`)، `raw_path`،
  `section`، `type` (paragraph/table/list/heading/mixed)، `offset` (إزاحة
  الحرف في الملف الأصلي)، `words`، `bytes`، `source_lines` [OBSERVED].

## 7. الفهرس (index) — BM25

- BM25 بايثون خالص، `k1=1.5` و`b=0.75` (افتراضيان موثقان، لا مضبوطان)
  [OBSERVED — `index.py`]. النص المفهرس لكل مقطع = breadcrumb القسم + نص
  المقطع [OBSERVED].
- حارس المصطلحات العامة (قاعدة موثقة): مصطلح يظهر في أكثر من نصف المقاطع
  لا يحمل دليلاً فيُتجاهل؛ فسؤال مكوّن من كلمات عامة فقط يسجّل 0 ويؤدي إلى
  «لا أعرف» [OBSERVED — `index.py: bm25_search`].
- التوكنايزر (`tokenize.py`): إزالة التشكيل والتطويل، توحيد أشكال الألف،
  `ة→ه` و`ى→ي` و`ؤ→و` و`ئ→ي`، تصغير اللاتينية، وحذف قائمة stopwords
  عربية/إنجليزية صغيرة. بلا تجذير (stemming) في v0.1 [OBSERVED].
- ملاحظة قياس: خط الأساس المقيس على هيثم استخدم `k1=1.2` و`b=0.75`
  [REPORTED — 12/15 rank-1]، بينما هذا الريبو يستخدم `k1=1.5`
  (افتراضي البايلوت) [OBSERVED] — المقارنة بينهما على نفس الـ corpus
  [NOT_RUN]؛ ونتائج هيثم نفسها غير قابلة لإعادة الإنتاج هنا لأن الـ corpus
  (5,896 صفحة) غائب [OBSERVED].
- الفهرس يُخزَّن في `index.json` مع بارامتراته، فيعيد `ask`/`eval` استخدام
  نفس البارامترات التي بُني بها [OBSERVED].

## 8. الماسترز (masters) — طبقة الويكي

- الماستر ملف عادي قابل للفهرسة والاستشهاد مثل أي مصدر [PROPOSED].
- **شرط مسبق**: سكيل صناعة الماسترز (`docs/skills/make-master/`) قبل أي
  ماستر جديد — الماسترز الـ 39 القديمة كل ماستر فيها 11 سطراً فقط (أقسام
  1/4/16)، و§4 مقطوع عند 5,000 حرف في 26/39، وروابط `[[Concept_...]]`
  مكسورة 100% (95/95)، ولا يوجد ماستر رئيسي واحد ولا خطوة موثقة لصنع
  ماستر [OBSERVED — دراسة الماسترز 2026-11-12].
- شكل الماستر الجديد: 3 أقسام (§1 خلاصة، §4 أنظمة، §16 إغلاق)، كل قسم سطر
  واحد تحت 5,000 حرف (السقف العلاجي 4,800 في السكيل)، وروابطه لمسارات
  حقيقية موجودة فعلاً أو تُحذف — لا روابط وهمية [REPORTED — من السكيل].
- خيارات معاذ الثلاثة لشكل الماستر (متخصص لكل مجلد / ضخم واحد / رئيسي +
  إحالة بالمسار) ما زالت مفتوحة كأسئلة دون حسم منه [REPORTED —
  process.md §6]؛ والافتراضي الموثق في السكيل: متخصص واحد لكل دومين له
  مادة خام [PROPOSED].
- `masters.py` [OBSERVED — كتبه وكيل متوازٍ أثناء بناء الـ CLI، والـ CLI
  يفوّض إليه بنجاح]: `build_masters(data_dir)` و`main(argv)` بخيار
  `--data DIR` فقط؛ يبني ماستراً واحداً لكل دومين + `masters/index.md`
  تحت `<data>/masters/`. قياس العينة [OBSERVED — 2026-11-12]:
  domains=4 masters=4 sources=20 chunks=151 links_verified=40
  links_dropped=0. ملاحظة: افتراض الـ CLI الأولي بوجود `--out` كان
  خاطئاً وصحّح في docstring في `cli.py` — الوحدة الحقيقية بلا `--out`.

## 9. السؤال (ask)

- استرجاع فقط، بلا توليد: الإجابة تجميع مقاطع مستشهدة (مسار خام + قسم +
  أسطر + chunk_id)؛ لا يُعاد صياغة المقطع كحقيقة [OBSERVED — `ask.py`].
- «لا أعرف» عند غياب الدليل: أفضل score ‏≤ `min-score` (افتراضي 0.0)
  [OBSERVED]. القيمة 0.0 افتراضي موثق لا عتبة مضبوطة [OBSERVED].
- التعارض: عرض الطرفين دائماً بلا حجر (قاعدة معاذ) — التفاصيل والحدود في
  `docs/CONTRADICTIONS.md` [REPORTED — من معاذ].
- Persona فلتر metadata اختياري (`--persona NAME`)؛ بلا مجلد `personas/`
  لا يوجد إلا `default` [OBSERVED].
- v0.1 استرجاع فقط بلا توليد [PROPOSED — phase2-research.md §4.5].

## 10. التقييم (eval)

- المقترح: 20 سؤالاً معروف الإجابة من محتوى العيّنة الفعلي + Recall@k +
  فحص الاستشهاد (هل المقطع المسترجع هو مصدر الإجابة فعلاً؟)
  [PROPOSED — phase2-research.md §4.2].
- مجموعة الأسئلة موجودة الآن: `examples/eval-questions.json` (20 سؤالاً:
  6 عناوين + 7 فقرة + 7 صياغات) [OBSERVED — كتبها وكيل eval].
- أول قياس على العينة [OBSERVED — 2026-11-12، عبر الـ CLI]:
  `n=20 rank-1=14 (0.700) top-3=15 (0.750) absent=5 skipped=0`
  (النافذة top-k=5 الافتراضية). وهذا قياس أول على عينة صغيرة، لا عتبة
  مضبوطة [PROPOSED]؛ وكل العتبات تبقى `null` حتى قياسين على نطاق أوسع
  (انظر THRESHOLDS.md).
- `eval.py` [OBSERVED — كتبه وكيل متوازٍ]: `evaluate(data_dir, questions,
  top_k=5, persona=None, min_score=0.0)` و`main(argv)` بخيارات
  `--data/--questions/[--top-k]/[--persona]/[--min-score]/[--out]` —
  مطابقة تماماً لافتراض الـ CLI الموثق في `cli.py`.

## 11. ما هو NOT_RUN (صريح)

- التضمين الكثيف + rerank: لم يُبنَ أبداً [NOT_RUN]. العائق المقيس هو
  الذاكرة (المتاح ~541MB وقت القياس؛ وموديل 1–2GB لا يُفتح) [OBSERVED —
  phase2-research.md §0]. المرشحان الوحيدان داخل الميزانية لاحقاً:
  `paraphrase-multilingual-MiniLM-L12-v2` (~118MB ONNX) و
  `intfloat/multilingual-e5-small` (~118MB ONNX) [REPORTED — بحث ويب] —
  ويُقاسان على أسئلة الصياغات التي فشل فيها BM25 (الرتب 28 و35) قبل أي
  اعتماد [PROPOSED].
- الجراف (GraphRAG/Cognee/RAGFlow): مؤجل لأسئلة علاقات فقط، بعد عمل
  الاسترجاع [PROPOSED]؛ وكمبادرة أولى مرفوض (ثقيل، LLM إلزامي للاستخراج،
  عربيته غير مثبتة، وفشل فعلياً في التجربة الوحيدة الموثقة)
  [REPORTED — phase2-research.md F-1..F-3].
- fine-tuning: مرفوض (غالٍ ولا يعطي استشهادات) [PROPOSED].
- نظام الادعاءات (Claims): مرفوض — عالج 3 من 2,541 فقط في wikillm
  [REPORTED]؛ والبديل هو الاستشهاد بالمقطع الخام [PROPOSED].
- RRF: عملية حسابية بسيطة تُنفَّذ فقط بعد وجود الضلعين (كلمات + كثيف)
  وقياسهما [PROPOSED — phase2-research.md F-10].

## 12. ما لا نفعله

- لا ننقل ملفات المستخدم ولا نبني vault جديداً [PROPOSED].
- لا ننشر ترجمات يوتيوب ولا نضمّن كوكيز في الكود [REPORTED].
- لا نفتح/نفهرس القسم `07/control` من أي أرشيف أبداً [OBSERVED — قاعدة مهمة].
- لا ندّعي نجاحاً قبل فحص القرص: كل ادعاء بأمر قياس [REPORTED — قاعدة
  «الدليل قبل الإعلان»].
