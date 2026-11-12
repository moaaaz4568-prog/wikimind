# wikimind

> نظام ويكي عام صغير يعمل محلياً: أي شخص عنده ملفات يحوّلها إلى «عقل»
> يستخرج منه المعرفة في أي وقت — باستشهاد بالمقطع الخام، لا من ذاكرة النموذج.

قاعدة الوسم في كل ادعاء واقعي في هذا الريبو: `OBSERVED` = قيس/شوهد بنفسه ·
`REPORTED` = منقول من وثيقة بلا إعادة تحقق · `PROPOSED` = استنتاج/توصية ·
`UNKNOWN` = لا دليل · `NOT_RUN` = لم يُفحص/لم يُشغَّل.

## لمن هذا؟

لأي شخص عنده ملفات (ملاحظات، مقالات، ترجمات، كتب بصيغة نصية) ويريد أن يسألها
فتجيبه من محتواها نفسه، مع ذكر المصدر حرفياً [PROPOSED — هدف المشروع كما
حدده معاذ: «عايز الويكي دي تتحول لراج… يبحث ويلاقي كلامهم ومعرفتهم فورا»].

لا حاجة لخادم، ولا حساب، ولا مفتاح API، ولا إنترنت بعد التنزيل [OBSERVED —
النظام يعمل بالكامل على ملفات محلية في هذه الجلسة].

## المتطلبات

- Python 3.10+ [PROPOSED — الإصدار المستهدف؛ ما قيس هنا هو Python 3.12.3]
- المكتبة القياسية فقط (stdlib) — **بلا تثبيت، بلا اعتماديات** [OBSERVED —
  كل وحدات `src/wikimind/` تستورد `argparse`/`json`/`re`/`math`/`hashlib` فقط]
- ملفاتك تبقى حيث هي: الروتر يشاور على مجلداتك كما هي، لا ينقل ملفاً واحداً
  [PROPOSED — قرار ملزم من دراسة يوتيوب §5]

## التدفق خطوة بخطوة

```
ملفاتك (.md / .txt) في مجلد واحد
  │  ingest   جرد + manifest.jsonl (مسار، sha256، بايت، كلمات، persona)
  │            + dedupe بالمحتوى + تسجيل المستبعدين
  ▼
terms         استخراج مصطلحات TF-IDF + مفاهيم من العناوين (خطوة مستقلة)
  │  masters  ماستر مضغوط لكل دومين له مادة خام (سكيل صناعة الماسترز —
  │            شرط مسبق لطبقة الويكي، انظر docs/DESIGN.md)
  ▼
chunk         تقطيع هيكلي: عنوان/فقرة/جدول/قائمة، مع metadata
  │            (المجموعة، مسار الخام، العنوان، البصمة)
  ▼
index         فهرس BM25 (بايثون خالص، k1=1.5 وb=0.75 كافتراضيين موثقين)
  ▼
ask           سؤال → مقاطع خام مستشهدة + «لا أعرف» عند غياب الدليل
  │            + عرض الطرفين عند التعارض، بلا حجر
  ▼
eval          قياس على أسئلة معروفة الإجابة (Recall@k + فحص الاستشهاد)
```

القياس هو البوابة الوحيدة: لا بوابات G0–G8 ولا حوكمة [PROPOSED — قرار ملزم].

الأمر الموحّد (من جذر الريبو):

```bash
PYTHONPATH=src python3 -m wikimind <command> [options]
# أو مباشرة كسكريبت:
python3 src/wikimind/cli.py <command> [options]
```

الأوامر: `ingest` · `chunk` · `index` · `terms` · `masters` · `ask` · `eval` ·
`build` (يشغّل ingest→chunk→index→terms→masters بالتسلسل، ويتوقف عند أول فشل).
كل أمر يفوّض لوحدة الموديول المقابلة عبر `main(argv)` الخاصة بها، فالخيارات هي
نفسها الموثقة في docstring كل وحدة [OBSERVED — انظر `src/wikimind/cli.py`].

## مثال على العينة

العينة `examples/sample-corpus/` [OBSERVED — 20 ملفاً: 17 مفهوم `CPT_*` و3
مفاهيم `C_*` عن الأوتريتش والمبيعات والمحتوى]:

```bash
PYTHONPATH=src python3 -m wikimind ingest --corpus examples/sample-corpus --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind chunk --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind index --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind terms --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind masters --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind ask "ما هي التدفئة warmup قبل الإرسال؟" --data /tmp/wikimind-data
PYTHONPATH=src python3 -m wikimind eval --data /tmp/wikimind-data --questions examples/eval-questions.json --out /tmp/wikimind-eval.json
```

النتائج المقيسة على العينة في هذه الجلسة [OBSERVED — 2026-11-12]:

```
ingest: found=20 kept=20 total_bytes=60964
chunk:  chunks=151
index:  N=151 terms=2023 avgdl=38.9
terms:  docs=20 global_terms=60 concepts=134
masters: domains=4 masters=4 sources=20 chunks=151 links_verified=40 links_dropped=0
         (Master_Content.md, Master_General.md, Master_Outbound.md, Master_Sales.md + index.md)
ask:    5 مقاطع، أفضل score=10.246، query ≈ 6 ms، والمقطع الأول من
        CPT_CURATED_OUTBOUND_WARMUP.md (أسطر 2–3) مستشهِداً حرفياً
        بإعداد Matthew («أسبوعين على الأقل») وSmartlead («0–30 رسالة يومياً»)
eval:   n=20 rank-1=14 (0.700) top-3=15 (0.750) absent=5 skipped=0
        (على أسئلة examples/eval-questions.json — 6 عناوين + 7 فقرة + 7 صياغات)
```

انظر `QUICKSTART.md` للطريق كاملاً نسخاً ولصقاً مع المخرجات المتوقعة.

## ملخص القرارات (ملزمة — لا تُعاد فتحها)

| القرار | المصدر |
|---|---|
| BM25 أولاً، stdlib، بلا اعتماديات | [REPORTED — قياس هيثم: 12/15 rank-1 و14/15 top-3 على 210 صفحة؛ والعناوين 4/4] |
| تقطيع هيكلي + metadata (المجموعة، مسار الخام، العنوان، البصمة) | [REPORTED — سياسة التقطيع R-2 في phase2-research.md] |
| شكل الحزمة OKF وروتر يشاور على المجلدات كما هي — لا نقل للملفات | [PROPOSED — من STUDY-REPORT.md §5] |
| سكيل صناعة الماسترز شرط مسبق لطبقة الويكي (روابط الماسترز القديمة مكسورة 100%: 95/95) | [OBSERVED — دراسة الماسترز 2026-11-12] |
| سؤال باستشهاد خام حرفي + «لا أعرف» عند غياب الدليل + عرض الطرفين عند التعارض بلا حجر | [REPORTED — من معاذ نفسه] |
| الكثيف + rerank لاحقاً فقط، بأصغر نموذج ONNX | [PROPOSED — phase2-research.md §4.3] |
| يوتيوب ← RAG عبر yt-dlp مع ملف كوكيز خارجي فقط | [REPORTED — 144/144 فيديو جُلبت ترجماتها بهذه الوصفة] |
| لا GraphRAG ولا fine-tuning ولا حوكمة ولا بوابات G0–G8 | [REPORTED — فشل Cognee/RAGFlow/GraphRAG موثق في phase2-research.md §2] |

## ماذا يوجد في الريبو

```
src/wikimind/     tokenize.py, ingest.py, chunk.py, index.py, terms.py,
                  masters.py, ask.py, eval.py, cli.py, __main__.py
docs/             DESIGN.md, THRESHOLDS.md, CONTRADICTIONS.md, YOUTUBE.md,
                  EVAL.md (من وكيل eval — لم أكتبه)
docs/skills/      make-master/ — سكيل صناعة الماسترز (شرط مسبق لطبقة الويكي)
examples/         sample-corpus/ (20 ملفاً) — العينة الوحيدة المقيسة
                  eval-questions.json (20 سؤالاً — من وكيل eval)
tests/            test_masters.py, test_eval.py (من الوكيلين المالكين)
```

## NOT_RUN — صراحةً

- `masters` و`eval`: كُتبا أثناء بناء هذه الواجهة (وكيلان متوازيان) والـ CLI
  يفوّض إليهما بنجاح [OBSERVED — قياس 2026-11-12: masters أنتجت 4 ماسترز،
  وeval قاس n=20 فكانت rank-1=0.700 وtop-3=0.750]. والـ CLI يحتفظ بمسار
  الرجوع: إن غاب أي ملف مستقبلاً يعيد الأمر كود 2 برسالة NOT_RUN واضحة
  بدل traceback [OBSERVED — `cli.py: _dispatch`].
- التضمين الكثيف + rerank: لم يُبنَ أبداً [NOT_RUN].
- الجراف (GraphRAG): لم يُبنَ [NOT_RUN].
- مجموعة أسئلة أكبر من الـ 20 سؤالاً، وكل عتبة رقمية كقيمة مضبوطة: `null`
  حتى تُقاس على نطاق أوسع (انظر `docs/THRESHOLDS.md` — أول قياس على
  العينة موجود الآن: rank-1=0.700 وtop-3=0.750 على n=20).
- شكل OKF على محتوى عربي، والريبو على ملفات مستخدم عشوائي: لم يُختبرا
  [NOT_RUN].
- لا يوجد أي push/upload إلى GitHub من هذه الجلسة [OBSERVED — ممنوع بدون إذن
  صريح من معاذ].

## قواعد أمان مطبقة في الكود

- القسم `07/control` (أو أي مجلد `control`) وأي ملف شكله سر/اعتماد (`*secret*`،
  `*token*`، `*.pem`، `*.key`…) لا يُقرأ ولا يُفهرس أبداً [OBSERVED —
  `ingest.py: is_secret_or_control`].
- لا كوكيز ولا توكنات داخل الكود أبداً — الكوكيز ملف خارجي فقط (يوتيوب)
  [REPORTED — تحفظ أمني موثق في STUDY-REPORT.md §3.7].
- لا نشر لترجمات يوتيوب (حقوق أصحابها) [REPORTED].
