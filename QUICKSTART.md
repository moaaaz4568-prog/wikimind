# QUICKSTART — من الصفر إلى أول سؤال مستشهد في ~دقيقة

> انسخ الأوامر كما هي من جذر الريبو. كل الأرقام أدناه مقيسة فعلاً على العينة
> في هذه الجلسة [OBSERVED — 2026-11-12، Python 3.12.3]، لا توقعات.

## 1. تأكد من بايثون

```bash
python3 --version   # 3.10+ مطلوب؛ المقيس هنا 3.12.3
```

لا شيء يُثبَّت: stdlib فقط [OBSERVED].

## 2. ابنِ خط الأنابيب على العينة

```bash
cd ~/workspace/wiki-system-repo
export PYTHONPATH=src

python3 -m wikimind ingest --corpus examples/sample-corpus --data /tmp/wikimind-data
python3 -m wikimind chunk --data /tmp/wikimind-data
python3 -m wikimind index --data /tmp/wikimind-data
python3 -m wikimind terms --data /tmp/wikimind-data
python3 -m wikimind masters --data /tmp/wikimind-data
python3 -m wikimind eval --data /tmp/wikimind-data --questions examples/eval-questions.json --out /tmp/wikimind-eval.json
```

المخرجات المتوقعة [OBSERVED]:

```
found=20 kept=20 duplicates_skipped=0 pointer_or_too_small_skipped=0 control_or_secret_excluded=0 total_bytes=60964
manifest: /tmp/wikimind-data/manifest.jsonl
skipped:  /tmp/wikimind-data/skipped.jsonl
chunks=151 -> /tmp/wikimind-data/chunks.jsonl
N=151 terms=2023 avgdl=38.9 -> /tmp/wikimind-data/index.json
docs=20 global_terms=60 concepts=134 -> /tmp/wikimind-data/terms.json + terms.md
domains=4 masters=4 sources=20 chunks=151 links_verified=40 links_dropped=0 -> /tmp/wikimind-data/masters/index.md
n=20 rank-1=14 (0.700) top-3=15 (0.750) absent=5 skipped=0 -> /tmp/wikimind-eval.json
```

ملفات البيانات كلها في `/tmp/wikimind-data/` (خارج الريبو عمداً — ملفاتك
الأصلية في `examples/sample-corpus/` لم تُمسّ ولم تُنقل) [OBSERVED].

## 3. اسأل أول سؤال — مع استشهاد

```bash
python3 -m wikimind ask "ما هي التدفئة warmup قبل الإرسال؟" --data /tmp/wikimind-data
```

المخرج المتوقع [OBSERVED — أول مقطعين حرفياً]:

```
السؤال: ما هي التدفئة warmup قبل الإرسال؟
النتائج: 5 مقطع (query: 6 ms)

ملاحظة: أحد المصادر يسجّل توتراً/تعارضاً موثقاً في قسم التوترات — راجعه مع النتائج.
======================================================================
[1] score=10.246 | التدفئة كإعداد معلن لا كرقم موحّد › الجوهر والآلية
    المصدر: CPT_CURATED_OUTBOUND_WARMUP.md (أسطر 2–3) | chunk: d6bcf596ca6d-0001 | domain: outbound | persona: default
    التدفئة هنا عملية تدريجية مرتبطة بسمعة الحساب قبل الحملة، لكن المصادر لا تقدم وصفة واحدة: Matthew يعرض أسبوعين على الأقل قبل الإرسال (**CLM_CURATED_OUTBOUND_WARMUP_001**)، ودليل Smartlead يصف إعدادًا من صفر إلى 30 رسالة يوميًا مع أكثر من عشرة نطاقات وصندوقين لكل نطاق (**CLM_CURATED_OUTBOUND_WARMUP_002**).
----------------------------------------------------------------------
[2] score=8.805 | ... › توترات وعدم توحيد
    ...سجل الدليل ثلاث توصيات/أوصاف مختلفة بدل دمجها...
```

## 4. جرّب «لا أعرف»

```bash
python3 -m wikimind ask "zzqqxx nonsense query" --data /tmp/wikimind-data
```

المخرج المتوقع [OBSERVED]:

```
لا أعرف — لا يوجد دليل (أفضل score = 0)
```

## 5. جرّب عرض الطرفين

```bash
python3 -m wikimind ask "كم رسالة إيميل في اليوم؟" --data /tmp/wikimind-data --both-sides
```

المخرج المتوقع [OBSERVED — يظهر شريط «طرفان مختلفان في المصادر — لا حجر،
نعرض الطرفين» ثم المقاطع الأربعة الأولى بأفضل score=3.641]. القيد الحالي:
الكشف رقمي خشن — يجمّع أي أرقام تشترك في كلمة وحدة (انظر
`docs/CONTRADICTIONS.md` §3)، فاقرأ المقاطع نفسها قبل تصديق الشريط.

## 6. ماذا بعد؟

- على ملفاتك أنت: بدّل `--corpus examples/sample-corpus` بمجلد ملفاتك
  (`.md`/`.txt`) وأعد الخطوات 2–3 — الملفات تُقرأ من مكانها ولا تُنقل
  [PROPOSED]. واختصار الخطوات بـ `build`:
  `python3 -m wikimind build --corpus <مجلدك> --data /tmp/wikimind-data`
  [OBSERVED — يعمل كاملاً: ingest→chunk→index→terms→masters].
- أوامر `masters` و`eval` تعمل الآن عبر الـ CLI [OBSERVED — قُيست أعلاه].
- لا تبنِ corpus يوتيوب قبل أن يعمل هذا الخط على ملفات محلية
  [PROPOSED — انظر `docs/YOUTUBE.md`].
