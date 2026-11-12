---
type: concept
concept_id: CPT_CURATED_OUTBOUND_POSTREPLY
title: "فجوة ما بعد الرد: تحويل الاهتمام إلى مسار قابل للقياس"
status: reviewed
claim_refs: [CLM_CURATED_OUTBOUND_POSTREPLY_001, CLM_CURATED_OUTBOUND_POSTREPLY_002, CLM_CURATED_OUTBOUND_POSTREPLY_003]
source_refs: [SRC_NEW_e84661b9d7960c58_d748e925]
related_concepts: [CPT_CURATED_OUTBOUND_METRICS, CPT_CURATED_OUTBOUND_OPS]
created: 2026-10-07
updated: 2026-10-07
---

## التعريف والآلية
فجوة ما بعد الرد هي المسافة بين positive reply وبين qualified attended meeting ثم close. يضع المصدر هدف سرعة رد أقل من 15 دقيقة في ساعات العمل (**CLM_CURATED_OUTBOUND_POSTREPLY_001**)، ويقسم المسؤوليات والمراحل (**CLM_CURATED_OUTBOUND_POSTREPLY_002**, **CLM_CURATED_OUTBOUND_POSTREPLY_003**).

## الشروط
السرعة هدف تشغيلي لا عقد؛ كما أن التخصيص يظل جزءًا من جودة الرد بحسب المصدر (**CLM_CURATED_OUTBOUND_POSTREPLY_001**). يجب أن يعرف العميل والوكالة من يحجز الاجتماع ومن يدير الحضور والإغلاق (**CLM_CURATED_OUTBOUND_POSTREPLY_003**).

## حدود وفشل
الرد المنسوخ قد يفشل في السياق الذي يحذر منه المصدر (**CLM_CURATED_OUTBOUND_POSTREPLY_001**). كما أن عدّ positive replies وحدها يخفي المراحل التي لا تُقاس إلا بالحجز والحضور والإغلاق (**CLM_CURATED_OUTBOUND_POSTREPLY_002**, **CLM_CURATED_OUTBOUND_POSTREPLY_003**).

## تطبيق مشروط
استخدم صفًا لكل lead يحفظ وقت الرد، مالك المرحلة التالية، ونتيجة meeting booked/show/qualified/close. هذا تصميم تشغيل مستنتج من مراحل المصدر، وليس claim عن أداء متوقع.

## سجل الأدلة
| Claim | المصدر |
|---|---|
| [CLM_CURATED_OUTBOUND_POSTREPLY_001](../claims/CLM_CURATED_OUTBOUND_POSTREPLY_001.md) | [Smartlead post-reply](../sources/SRC_NEW_e84661b9d7960c58_d748e925.md) |
| [CLM_CURATED_OUTBOUND_POSTREPLY_002](../claims/CLM_CURATED_OUTBOUND_POSTREPLY_002.md) | [Smartlead post-reply](../sources/SRC_NEW_e84661b9d7960c58_d748e925.md) |
| [CLM_CURATED_OUTBOUND_POSTREPLY_003](../claims/CLM_CURATED_OUTBOUND_POSTREPLY_003.md) | [Smartlead post-reply](../sources/SRC_NEW_e84661b9d7960c58_d748e925.md) |
