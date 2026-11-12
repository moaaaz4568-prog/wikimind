# MEASUREMENTS — القياسات النهائية لخط wikimind (جولة تحقق وقياس)

> تاريخ القياس: 2026-11-12 [OBSERVED — كل الأرقام في هذا الملف من أوامر
> شُغّلت فعلاً في هذه الجولة، على العينة `examples/sample-corpus/`].
> قاعدة الوسم: `OBSERVED` = قيس/شوهد بنفسه · `REPORTED` = منقول من وثيقة
> بلا إعادة تحقق · `PROPOSED` = استنتاج/توصية · `UNKNOWN` = لا دليل ·
> `NOT_RUN` = لم يُفحص/لم يُشغَّل. لا رقم هنا مخترع: كل رقم مصدره أمر
> موثق في §2.

قرارات ملزمة مطبقة في القياس [REPORTED — من
`~/workspace/wiki-rag-youtube-research/STUDY-REPORT.md` §6]: BM25 أولاً
stdlib بلا اعتماديات؛ استشهاد خام حرفي + «لا أعرف» عند غياب الدليل +
عرض الطرفين عند التعارض بلا حجر؛ لا GraphRAG ولا fine-tuning ولا
بوابات G0–G8 — القياس هو البوابة الوحيدة.

## 1. البيئة [OBSERVED]

| البند | القيمة المقيسة | الأمر |
|---|---|---|
| Python | 3.12.3 | `python3 --version` |
| الذاكرة الكلية | 7,934 MB | `free -m` |
| الذاكرة المتاحة وقت القياس | 435 MB (الحر 179 MB) | `free -m` |
| المعالجات | 4 | `nproc` |
| حجم العينة | 20 ملفاً، 60,964 بايت | `ingest` |

ملاحظة الذاكرة [PROPOSED — استنتاج من الرقم المقيس]: المتاح 435 MB
فقط وقت القياس، فيؤكد تأجيل التضمين الكثيف (نموذج 1–2 GB لا يُفتح
هنا) كما في `docs/DESIGN.md` §11؛ والمرشحان الصغيران (~118 MB ONNX)
ما زالا غير مبنيين [NOT_RUN].

## 2. أوامر التشغيل كاملة [OBSERVED — نُفّذت حرفياً من جذر الريبو]

```bash
cd ~/workspace/wiki-system-repo
# 1) اختبارات الوحدة
PYTHONPATH=src python3 -m unittest discover -s tests -v
# 2) خط الأنابيب كاملاً من الصفر (بيانات في /tmp فقط)
PYTHONPATH=src python3 -m wikimind build --corpus examples/sample-corpus --data /tmp/wm-e2e
PYTHONPATH=src python3 -m wikimind masters --data /tmp/wm-e2e   # إعادة مستقلة بعد build
PYTHONPATH=src python3 -m wikimind eval --data /tmp/wm-e2e --questions examples/eval-questions.json --out /tmp/wm-e2e-eval.json
# 3) أسئلة يدوية عبر ask (انظر §5)
PYTHONPATH=src python3 -m wikimind ask "خنق معدل الإرسال Send-Rate Throttle" --data /tmp/wm-e2e --json
PYTHONPATH=src python3 -m wikimind ask "قد إيه أجهز حساب الإرسال الجديد قبل ما أبدأ حملتي الأولى؟" --data /tmp/wm-e2e --json
PYTHONPATH=src python3 -m wikimind ask "zzqqxx nonsense query" --data /tmp/wm-e2e
PYTHONPATH=src python3 -m wikimind ask "كم رسالة إيميل في اليوم؟" --data /tmp/wm-e2e --both-sides
# 4) تحقق روابط الماسترز (سكريبت بايثون مؤقت في /tmp، حُذف بعد التشغيل)
#    يفحص كل مسار بين backticks وكل رابط [..](./..) في masters/*.md ويتحقق من وجوده على القرص
# 5) تحقق QUICKSTART حرفياً (§7): نفس أوامره نسخاً ولصقاً على /tmp/wikimind-data
```

لا بيانات تُركت داخل الريبو [OBSERVED]: مجلدا البيانات `/tmp/wm-e2e`
و`/tmp/wikimind-data` (356K لكل منهما) وتقرير التقييم
`/tmp/wm-e2e-eval.json` و`/tmp/wikimind-eval.json` — كلها في `/tmp`.

## 3. اختبارات الوحدة [OBSERVED]

الأمر: `PYTHONPATH=src python3 -m unittest discover -s tests -v`
(أعيد تشغيله بعد إصلاحات التكامل في §8 فبقيت النتيجة نفسها).

```
Ran 18 tests in 0.131s — OK (18/18، صفر فشل)
  tests/test_eval.py     9/9  (عنوان rank-1، بلا تداخل مصطلحات → لا نتائج،
                               عدّ ومعدلات 3/4، مشوهة تُتخطى، persona وmin-score،
                               JSON ذهاباً وإياباً، CLI: stdout و--out ومجلد مفقود → 2)
  tests/test_masters.py  9/9  (ماستر لكل دومين، كل مسار موجود على القرص،
                               index.md يشاور على ماسترز موجودة، بنية §1/§4/§16
                               تحت 5,000 حرف، استشهاد بمقاطع الدومين، CLI
                               وإعادة التشغيل، مجلد مفقود → 2)
```

لا إصلاح كان مطلوباً في الاختبارات أو الوحدات [OBSERVED — مرت كلها
من أول تشغيل].

## 4. خط الأنابيب الكامل من الصفر [OBSERVED]

الأمر: `PYTHONPATH=src python3 -m wikimind build --corpus
examples/sample-corpus --data /tmp/wm-e2e` — خرج 0.

```
[build] ingest --corpus examples/sample-corpus --data /tmp/wm-e2e
found=20 kept=20 duplicates_skipped=0 pointer_or_too_small_skipped=0 control_or_secret_excluded=0 total_bytes=60964
[build] chunk --data /tmp/wm-e2e --max-words 800
chunks=151 -> /tmp/wm-e2e/chunks.jsonl
[build] index --data /tmp/wm-e2e
N=151 terms=2023 avgdl=38.9 -> /tmp/wm-e2e/index.json
[build] terms --data /tmp/wm-e2e --top-n 15
docs=20 global_terms=60 concepts=134 -> /tmp/wm-e2e/terms.json + terms.md
[build] masters --data /tmp/wm-e2e
domains=4 masters=4 sources=20 chunks=151 links_verified=40 links_dropped=0 -> /tmp/wm-e2e/masters/index.md
[build] done -> /tmp/wm-e2e
```

إعادة `masters` مستقلة بعد `build` أعطت السطر نفسه حرفياً
[OBSERVED — خروج 0]، والماسترز الأربعة:
`Master_Content.md`، `Master_General.md`، `Master_Outbound.md`،
`Master_Sales.md` + `index.md`.

## 5. التقييم على أسئلة العينة [OBSERVED]

الأمر: `python3 -m wikimind eval --data /tmp/wm-e2e --questions
examples/eval-questions.json --out /tmp/wm-e2e-eval.json` — خرج 0.

```
n=20 rank-1=14 (0.700) top-3=15 (0.750) absent=5 skipped=0
```

| النوع | العدد | rank-1 | top-3 |
|---|---|---|---|
| title | 6 | 6/6 (1.000) | 6/6 (1.000) |
| paragraph | 7 | 7/7 (1.000) | 7/7 (1.000) |
| paraphrase | 7 | 1/7 (0.143) | 2/7 (0.286) |
| **الإجمالي** | **20** | **14/20 (0.700)** | **15/20 (0.750)** |

الغائبون الخمسة كلهم paraphrase [OBSERVED — من تقرير JSON]:

| السؤال (مختصر) | الملف المتوقع | rank | top-1 الفعلي |
|---|---|---|---|
| كيف أخلي بداية رسالتي قصيرة وواضحة…؟ | CPT_CURATED_CONTENT_HOOK_CLARITY.md | 3 (في top-3) | CPT_CURATED_SALES_OFFER_CLARITY.md |
| ليه العميل ما يشتريش حتى لو العرض كويس؟ | C_Trust_Precedes_Transaction.md | غائب (null) | CPT_CURATED_SALES_PROBLEM_DIAGNOSIS.md |
| قد إيه أجهز حساب الإرسال الجديد…؟ | CPT_CURATED_OUTBOUND_WARMUP.md | غائب (null) | CPT_CURATED_SALES_VALUE_PRICING.md |
| كام مرة أتابع اللي ما ردش…؟ | CPT_CURATED_OUTBOUND_FOLLOWUP.md | غائب (null) | CPT_CURATED_OUTBOUND_MULTICHANNEL.md |
| بعد رد العميل على الإيميل، أعمل إيه…؟ | CPT_CURATED_OUTBOUND_MULTICHANNEL.md | غائب (null) | C_Send_Rate_Throttle.md |
| إزاي أساعد العميل يختار بين خيارين…؟ | CPT_CURATED_SALES_CONSULTATIVE_CLOSING.md | غائب (null) | CPT_CURATED_CONTENT_POSITIONING.md |

والصياغة السابعة نجحت rank-1 («إيه الأجزاء اللي بيتكون منها نظام
الإيميل البارد…؟» → `CPT_NEW_OUTBOUND_COLD_EMAIL_SYSTEM.md`)،
فـ paraphrase: rank-1 = 1/7 وtop-3 = 2/7 [OBSERVED]. النمط مطابق
للمقيس قديماً على هيثم (عناوين قوية، صياغات ضعيفة) [REPORTED]،
و«غائب» تعني خارج نافذة top-5 لا غير موجود في الفهرس [PROPOSED —
قاعدة موثقة في `eval.py`].

الأرقام مطابقة تماماً لما وثّقته `README.md` و`docs/EVAL.md` §4
(0.700 / 0.750) [OBSERVED — إعادة قياس مستقلة بنفس الأوامر].

## 6. أسئلة `ask` اليدوية [OBSERVED]

كلها على `/tmp/wm-e2e` (الفهرس نفسه من §4)، بخيار `--json` حيث
ذُكر score رقمياً، وبدونه حيث ذُكر النص الحرفي.

### (أ) سؤال عنوان حرفي

الأمر: `ask "خنق معدل الإرسال Send-Rate Throttle" --json`

- النتائج: 5 مقاطع، `no_evidence=false`.
- **أعلى score = 35.504، المقطع الأول من `C_Send_Rate_Throttle.md`
  (أسطر 2–2)**، والثاني والثالث من الملف نفسه (14.058 ثم 12.678).
- الملف المتوقع جاء أولاً [OBSERVED].

### (ب) سؤال معاد صياغته

الأمر: `ask "قد إيه أجهز حساب الإرسال الجديد قبل ما أبدأ حملتي الأولى؟" --json`

- النتائج: 5 مقاطع، `no_evidence=false`.
- **أعلى score = 5.824، المقطع الأول من
  `CPT_CURATED_SALES_VALUE_PRICING.md`** — ملف خاطئ؛ الملف المتوقع
  `CPT_CURATED_OUTBOUND_WARMUP.md` غائب عن أول 5 نتائج (الثاني
  `CPT_CURATED_OUTBOUND_INFRASTRUCTURE.md` بـ 4.167، والثالث
  `C_Send_Rate_Throttle.md` بـ 3.952).
- متسق مع §5 (هذا السؤال rank=null في التقييم) [OBSERVED].

### (ج) سؤال بلا دليل إطلاقاً

الأمر: `ask "zzqqxx nonsense query"`

- المخرج حرفياً: `لا أعرف — لا يوجد دليل (أفضل score = 0)` [OBSERVED].

### (د) سؤال تعارض مع `--both-sides`

الأمر: `ask "كم رسالة إيميل في اليوم؟" --both-sides`

- النتائج: 4 مقاطع، `no_evidence=false`، **أعلى score = 3.641،
  المقطع الأول من `CPT_CURATED_OUTBOUND_TARGETING.md` (أسطر 11–12)**.
- شريط التعارض ظهر: `⚠️ طرفان مختلفان في المصادر — لا حجر، نعرض
  الطرفين:` مع أطراف `6 per-day` و`1 per-day` و`10 per-day` من ملفات
  مختلفة، ثم «القرار للمستخدم؛ الأرقام كما وردت في مصادرها»
  [OBSERVED].
- قيد موثق: الكشف رقمي خشن — يجمّع أي أرقام تشترك في وحدة واحدة،
  و«6 per-day» تكرر من 3 ملفات مختلفة كطرف واحد [OBSERVED —
  `docs/CONTRADICTIONS.md` §3 و`QUICKSTART.md` §5].

### سؤال مرجعي إضافي (من QUICKSTART §3)

الأمر: `ask "ما هي التدفئة warmup قبل الإرسال؟"` — أعلى score =
**10.246**، المقطع الأول من `CPT_CURATED_OUTBOUND_WARMUP.md`
(أسطر 2–3)، والثاني 8.805 من الملف نفسه، وزمن الاستعلام 5.4 ms
(في تشغيل QUICKSTART الحرفي: 7 ms) [OBSERVED].

## 7. تحقق روابط الماسترز المولدة [OBSERVED]

سكريبت تحقق (بايثون، في `/tmp` وحُذف بعد التشغيل): قرأ كل ملفات
`masters/*.md` الخمسة في `/tmp/wm-e2e/masters/`، واستخرج كل مسار بين
backticks (`/abs/path/*.md` و`./Master_*.md` و`masters/...`) وكل رابط
`[..](./..)`، وتحقّق من وجود كل هدف على القرص بـ `os.path.isfile`.

```
files_checked=5 paths_checked=81 missing=0
index_links=4 index_missing=0
```

- **81 مساراً مذكوراً، 0 مفقود — كل روابط الماسترز موجودة فعلاً على
  القرص** [OBSERVED]. متسق مع `links_verified=40 links_dropped=0` من
  `masters.py` (الـ 81 تشمل مسارات §16 المصادر + روابط `index.md` +
  مسار الماستر نفسه المذكور في سطره الثاني؛ أي عدّ أوسع من عدّ
  الوحدة، وكلاهما صفر مكسور).
- ملاحظة منهجية: اختبارات `tests/test_masters.py` تفحص الشيء نفسه
  على عينة ملفين (9/9 ناجحة، §3) [OBSERVED].

## 8. توحيد عقود التكامل + الإصلاحات [OBSERVED]

### ما تحقق منه

- `__main__.py` ملف واحد سليم يفوّض إلى `cli.main` (لا توجد نسخة
  ثانية متعارضة — `find . -name "__main__.py"` أعاد ملفاً واحداً
  فقط)، ويعمل عبر `python3 -m wikimind` وعبر
  `python3 src/wikimind/cli.py` مباشرة (الأخير أعيد اختباره بعد
  الإصلاحات: خروج 0) [OBSERVED].
- العقود الفعلية: `build_masters(data_dir)` بلا `out_dir`، و
  `evaluate(data_dir, questions: list, top_k=5, persona=None,
  min_score=0.0)` بقائمة لا مسار، و`main(argv)` لكل وحدة بالخيارات
  الموثقة — و`cli.py` يفوّض إليها بمطابقة تامة [OBSERVED].

### إصلاحات التكامل (تعديلات صغيرة موضعية، مع السبب)

1. **`src/wikimind/cli.py` — docstring** [OBSERVED]: كان يحتوي كتلة
   «Assumptions about the two modules not yet written… files
   `masters.py` and `eval.py` do not exist yet» مع افتراض خاطئ
   `build_masters(data_dir, out_dir=None)` و`--out`، رغم أن فقرة
   UPDATE تحته تصححها — فكان الملف يناقض نفسه. استُبدلت الكتلة
   والفقرة بعقد واحد موثّق `[OBSERVED — verified 2026-11-12]`
   يطابق التواقيع الفعلية. رسالة الرجوع `NOT_RUN` في `_dispatch`
   باقية كمسار رجوع فقط (إن غاب ملف مستقبلاً → خروج 2).
2. **`docs/DESIGN.md` §3** [OBSERVED]: مخطط خط الأنابيب كان يعلّم
   `masters` و`eval` بـ `(NOT_RUN)`، ويذكر `[--out DIR]` لـ masters
   لا يقبله الكود. صحّحا إلى `(OBSERVED — يعمل: …)` بالأرقام
   المقيسة، وحُذف `[--out DIR]`.
3. **`docs/EVAL.md` §7** [OBSERVED]: الفقرة الأخيرة كانت تقول إن
   docstring في `cli.py` و`README.md` «يحتاجان تحديثاً من المنسق»
   وإن `USAGE` يحوي «NOT_RUN: module not written yet» — غير دقيق
   بعد الآن (تلك العبارة في رسالة الرجوع `_NOT_WRITTEN` لا في
   `USAGE`). أعيدت صياغتها لتسجيل العقدين الموثّقين والإصلاح.

بعد الإصلاحات: `cli.py` يُحلَّل بنجاح (`ast.parse`)، واختبارات
الوحدة 18/18 (أعيدت)، و`masters` عبر الـ CLI خروج 0، و`grep` عن
«do not exist yet / not yet written / NOT_RUN: module» في `src/` و
`docs/DESIGN.md` و`docs/EVAL.md` و`README.md` و`QUICKSTART.md`
أعاد صفر نتيجة (عدا bytecode قديم حُذف مع `__pycache__`) [OBSERVED].

### ما لم يتغير

- لا وحدة أعيدت كتابتها ولا وحدة جديدة بُنيت؛ `masters.py` و
  `eval.py` و`ask.py` و`index.py` وغيرها لم تُمسّ [OBSERVED].
- `README.md` كان متسقاً أصلاً (NOT_RUN فيه يذكر أن masters/eval
  موجودان ومقيسان) فلم يُعدَّل [OBSERVED].
- `docs/THRESHOLDS.md` و`docs/YOUTUBE.md` و
  `docs/CONTRADICTIONS.md`: لا نص قديم فيها عن masters/eval
  [OBSERVED — grep].

## 9. تحقق QUICKSTART حرفي [OBSERVED]

نُفّذت أوامر `QUICKSTART.md` §§1–5 نسخاً ولصقاً من جذر الريبو على
`/tmp/wikimind-data` (بعد `rm -rf` له):

- §1: `python3 --version` → `3.12.3`، مطابق للموثق [OBSERVED].
- §2: أسطر المخرجات الستة مطابقة حرفياً للمتوقع في الوثيقة:
  `found=20 kept=20 … total_bytes=60964`، `chunks=151`،
  `N=151 terms=2023 avgdl=38.9`، `docs=20 global_terms=60
  concepts=134`، `domains=4 masters=4 … links_verified=40
  links_dropped=0`، `n=20 rank-1=14 (0.700) top-3=15 (0.750)
  absent=5 skipped=0` [OBSERVED].
- §3: سؤال التدفئة — أول مقطعين حرفياً كما في الوثيقة
  (score=10.246 ثم 8.805، `CPT_CURATED_OUTBOUND_WARMUP.md` أسطر
  2–3، نص Matthew/Smartlead نفسه)، مع ملاحظة التوتر نفسها؛ زمن
  الاستعلام 7 ms مقابل 6 ms في الوثيقة — فرق توقيت فقط، لا فرق
  محتوى [OBSERVED].
- §4: `لا أعرف — لا يوجد دليل (أفضل score = 0)` حرفياً [OBSERVED].
- §5: شريط الطرفين + أفضل score=3.641 + 4 مقاطع، كما في الوثيقة
  حرفياً [OBSERVED].

**النتيجة: QUICKSTART.md صحيح كاملاً كما هو، بلا أي تصحيح مطلوب**
[OBSERVED]. لا اختلاف واحد في أمر أو مخرج.

## 10. خلل بقي بلا حل

- لا خلل وظيفي بقي [OBSERVED — كل الأوامر المذكورة هنا خرجت 0،
  وكل المخرجات طابقت الموثق].
- الفجوة المعروفة الوحيدة هي فجوة القياس نفسها لا عطل: صياغات
  paraphrase العامية 1/7 rank-1 (§5) — وهذا ما يُفترض أن يغلقه
  تضمين كثيف لاحق بعد قياسه [PROPOSED]، وليس إصلاحاً لهذه الجولة.
- كشف التعارض الرقمي خشن (يجمّع أي أرقام تشترك في وحدة) — قيد
  موثق في `docs/CONTRADICTIONS.md` §3، لا عطل جديد [OBSERVED].

## 11. NOT_RUN — صريح

- التضمين الكثيف + rerank: لم يُبنَ أبداً [NOT_RUN].
- الجراف (GraphRAG): لم يُبنَ [NOT_RUN].
- فحص استشهاد آلي (هل المقطع المسترجع هو مصدر الإجابة فعلاً؟):
  لا يوجد [NOT_RUN — فُحص يدوياً هنا بسؤال واحد في §6، لا برقم].
- أسئلة «بلا دليل» كمجموعة تقييم، وقياس عرض الطرفين عند التعارض
  كمجموعة: لا توجد [NOT_RUN — مغطاة بسؤالين يدويين فقط في §6].
- زمن الاستعلام والذاكرة كقياس أداء منهجي: لم تُقاس إلا قيم مفردة
  (query 5.4–7 ms على سؤال التدفئة) [NOT_RUN كقياس منهجي].
- مجموعة أسئلة أكبر من 20، وأي عتبة رقمية كقيمة مضبوطة: `null`
  حتى تُقاس على نطاق أوسع [NOT_RUN].
- شكل OKF على محتوى عربي، والريبو على ملفات مستخدم عشوائي: لم
  يُختبرا [NOT_RUN].
- أرقام هيثم القديمة (12/15 rank-1، 14/15 top-3 على 210 صفحة):
  لا يمكن إعادة إنتاجها هنا — نصوص الأسئلة الـ 15 غير محفوظة
  [UNKNOWN] والـ corpus غائب [OBSERVED].
- لا push/upload إلى GitHub من هذه الجولة (ممنوع بدون إذن صريح)،
  والريبو المحلي نفسه ليس Git repo أصلاً (`git rev-parse` أعاد
  fatal: not a git repository) [OBSERVED].
- القسم `07/control` من أي أرشيف: لم يُفتح ولم يُفهرس إطلاقاً
  [OBSERVED — قاعدة أمان مطبقة في `ingest.py`].
