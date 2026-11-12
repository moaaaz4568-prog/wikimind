---
type: concept
concept_id: CPT_CURATED_OUTBOUND_METRICS
title: "من open إلى close: طبقات القياس التي لا يجوز خلطها"
status: reviewed
claim_refs: [CLM_CURATED_OUTBOUND_METRICS_001, CLM_CURATED_OUTBOUND_METRICS_002, CLM_CURATED_OUTBOUND_METRICS_003]
source_refs: [SRC_NEW_d31f6979a8434158_88533a54, SRC_NEW_0d7ec9deba74f6c9_45adb3fb, SRC_NEW_e84661b9d7960c58_d748e925]
related_concepts: [CPT_CURATED_OUTBOUND_POSTREPLY, CPT_CURATED_OUTBOUND_TARGETING]
created: 2026-10-07
updated: 2026-10-07
---

## الجوهر
هذه ليست أسماء مترادفة. المصدر يعرّف sends وreply rate وpositive reply rate وmeetings booked كطبقات منفصلة (**CLM_CURATED_OUTBOUND_METRICS_001**)، بينما يوضح Smartlead أن replies لا تساوي revenue وأن booking/show/close مراحل لاحقة (**CLM_CURATED_OUTBOUND_METRICS_003**).

## تمييز المؤشرات
- **Open rate:** حدث تحميل/فتح يصفه مصدر Instantly بأنه غير موثوق ويوصي بتجربة تعطيله (**CLM_CURATED_OUTBOUND_METRICS_002**).
- **Reply rate:** نسبة الردود إلى الإرسالات كما يشرح المصدر (**CLM_CURATED_OUTBOUND_METRICS_001**).
- **Positive reply:** رد يبدي اهتمامًا، لكنه ليس meeting ولا close؛ الفصل بينه وبين الاجتماع مطلوب في تعريف المؤشرات (**CLM_CURATED_OUTBOUND_METRICS_001**, **CLM_CURATED_OUTBOUND_METRICS_003**).
- **Meeting booked/show/close:** مراحل بعد الرد، ويُحذر المصدر من اعتبار الرد إيرادًا (**CLM_CURATED_OUTBOUND_METRICS_003**).

## حالات الفشل
التركيز على open قد يعطي صورة زائفة (**CLM_CURATED_OUTBOUND_METRICS_002**)، والتركيز على positive reply قد يخفي فشل الحجز أو الحضور أو الإغلاق (**CLM_CURATED_OUTBOUND_METRICS_003**). لا يثبت أي Claim هنا نسب تحويل أو معيارًا صناعيًا.

## تطبيق مشروط وسجل أدلة
أنشئ قمعًا منفصل الأعمدة، ولا تنقل metric من طبقة إلى أخرى. | Claim | المصدر |
|---|---|
| [CLM_CURATED_OUTBOUND_METRICS_001](../claims/CLM_CURATED_OUTBOUND_METRICS_001.md) | [Matthew metrics](../sources/SRC_NEW_d31f6979a8434158_88533a54.md) |
| [CLM_CURATED_OUTBOUND_METRICS_002](../claims/CLM_CURATED_OUTBOUND_METRICS_002.md) | [Instantly open tracking](../sources/SRC_NEW_0d7ec9deba74f6c9_45adb3fb.md) |
| [CLM_CURATED_OUTBOUND_METRICS_003](../claims/CLM_CURATED_OUTBOUND_METRICS_003.md) | [Smartlead post-reply](../sources/SRC_NEW_e84661b9d7960c58_d748e925.md) |
