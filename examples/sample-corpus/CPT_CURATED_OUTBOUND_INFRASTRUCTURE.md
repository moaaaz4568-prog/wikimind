---
type: concept
concept_id: CPT_CURATED_OUTBOUND_INFRASTRUCTURE
title: "بنية الإرسال التي تسبق تحسين النسخة"
status: reviewed
claim_refs: [CLM_CURATED_OUTBOUND_INFRA_001, CLM_CURATED_OUTBOUND_INFRA_002, CLM_CURATED_OUTBOUND_INFRA_003]
source_refs: [SRC_NEW_38da1c8079fa511c_ca23fa0b]
related_concepts: [CPT_CURATED_OUTBOUND_WARMUP, CPT_CURATED_OUTBOUND_METRICS]
created: 2026-10-07
updated: 2026-10-07
---

## الجوهر والآلية
المفهوم ليس «إرسالًا أكثر» بل ترتيب طبقات البنية قبل الحكم على العرض: مصادقة النطاق، بناء السمعة، ثم حماية القائمة من الارتدادات والتكرار. يدعم المصدر هذه الطبقات بتوصية المصادقة (**CLM_CURATED_OUTBOUND_INFRA_001**)، وبالتحذير من الإرسال الكثيف من نطاق جديد (**CLM_CURATED_OUTBOUND_INFRA_002**)، وبالتنظيف الأسبوعي (**CLM_CURATED_OUTBOUND_INFRA_003**).

## الشروط
- عند إنشاء نطاق إرسال جديد، تُقرأ توصية بناء السمعة كشرط سابق، لا كضمان وصول (**CLM_CURATED_OUTBOUND_INFRA_002**).
- عند إدارة قائمة نشطة، يكون التنظيف الأسبوعي ومراجعة الارتدادات إجراءً مشروطًا بوجود حجم وقائمة تستدعي ذلك (**CLM_CURATED_OUTBOUND_INFRA_003**).

## الحدود وحالات الفشل
إذا اعتُبرت SPF/DKIM/DMARC ضمانًا، أو اعتُبر نطاق جديد جاهزًا لمجرد شرائه، فهذه قفزة لا يثبتها الدليل. كذلك لا يسمح المقتطف الخاص بالقائمة بتحويل النسب التي ينسبها المتحدث إلى benchmark (**CLM_CURATED_OUTBOUND_INFRA_001**, **CLM_CURATED_OUTBOUND_INFRA_003**).

## توترات
المصدر يذكر استراتيجية IP مختلفة حسب الحجم داخل نفس المقتطف (**CLM_CURATED_OUTBOUND_INFRA_001**)، لذلك لا يصح نسخ إعداد المرسل الكبير إلى مرسل صغير بلا شرط الحجم.

## تطبيقات مشروطة
افصل في لوحة التشغيل بين «فشل المصادقة/السمعة» و«فشل الاستهداف/النسخة». نفّذ فحص السجلات ثم راقب الارتدادات والتكرارات قبل زيادة الإرسال؛ هذا تطبيق تنظيمي مشروط بالمقتطفات، وليس ادعاءً بأن الخطوات تضمن inbox.

## سجل الأدلة
| Claim | نوع الدليل | المصدر |
|---|---|---|
| [CLM_CURATED_OUTBOUND_INFRA_001](../claims/CLM_CURATED_OUTBOUND_INFRA_001.md) | direct quote، توصية المصادقة وIP | [Smartlead Deliverability](../sources/SRC_NEW_38da1c8079fa511c_ca23fa0b.md) |
| [CLM_CURATED_OUTBOUND_INFRA_002](../claims/CLM_CURATED_OUTBOUND_INFRA_002.md) | direct quote، نطاق جديد وسمعة | [المصدر](../sources/SRC_NEW_38da1c8079fa511c_ca23fa0b.md) |
| [CLM_CURATED_OUTBOUND_INFRA_003](../claims/CLM_CURATED_OUTBOUND_INFRA_003.md) | direct quote، تنظيف القائمة | [المصدر](../sources/SRC_NEW_38da1c8079fa511c_ca23fa0b.md) |
