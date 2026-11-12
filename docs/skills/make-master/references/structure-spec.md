# مواصفة هيكل الماستر — بالأرقام من الدراسة

> المصدر الوحيد للأرقام: `~/workspace/wiki-study/anatomy.md` و`variance-qa.md` و`raw-material.md`
> (قياسات على `NEXUS_BRAIN.md`، 39 ماستراً، مولّد 2026-07-19).
> كل رقم موسوم `OBSERVED` ما لم يُذكر خلافه. وسوم الادعاءات:
> `OBSERVED` = مقيس · `REPORTED` = منقول من نص ملف · `PROPOSED` = استنتاج ·
> `UNKNOWN` = لا دليل · `NOT_RUN` = لم يُقَس.

## 1. الملف ككل

| المقياس | القيمة | ملاحظة |
|---|---|---|
| عدد الماسترز | 39 بالضبط [OBSERVED] | `grep -c '^## Master_'` = 39، بلا مكرر |
| أسطر الملف | 434 سطراً [OBSERVED] | 435 عنصراً عند التقسيم |
| حجم الملف | 421,478 بايت / 269,304 حرفاً [OBSERVED] | |
| إجمالي الكلمات | 45,506 كلمة [OBSERVED] | عدّ `split()` على النص كما هو (بما فيه علامات Markdown) |
| كلمات الأقسام الثلاثة (§1+§4+§16) | 45,324 كلمة [OBSERVED] | الفرق 182 كلمة = الترويسات والمسارات والفواصل |
| الترويسة (سطر 1) | `# 🧠 NEXUS_BRAIN — 39-Master Compressed Brain` [OBSERVED] | |
| تاريخ التوليد (سطر 3) | `> Generated 2026-07-19 from active canonical files only.` [REPORTED] | نص الترويسة — لم يُتحقق من التاريخ بمصدر مستقل |
| سطر الاسترجاع (سطر 5) | `> 39 canonical masters. Deep retrieval: \`rag/query.py --master Master_Name --section N\`.` [REPORTED] | وجود `rag/query.py` فعلياً في الأرشيف NOT_RUN |

## 2. بنية الماستر الواحد: 11 سطراً، 3 أسطر محتوى

كل ماستر يشغل **11 سطراً بالضبط** [OBSERVED] (6 أسطر ترويسة + 39 × 11 = 435 عنصراً بعد التقسيم):

| سطر داخل الماستر | المحتوى |
|---|---|
| 1 | `## Master_<Name>` |
| 2 | مسار المصدر بين backticks: `` `NN_topic/Master_Name.md` `` |
| 3 | سطر فارغ |
| 4 | القسم §1 — **سطر واحد طويل جداً** |
| 5 | سطر فارغ |
| 6 | القسم §4 — **سطر واحد طويل جداً** |
| 7 | سطر فارغ |
| 8 | القسم §16 — **سطر واحد طويل جداً** |
| 9 | سطر فارغ |
| 10 | فاصل `---` |
| 11 | سطر فارغ |

**قاعدة هيكلية 1:** الماستر ليس ملفاً متعدد الأسطر، بل **3 أسطر محتوى عملاقة** (كل قسم = سطر واحد) محاطة بأسطر فارغة وفاصل `---`. أي أداة تعالج الملف سطراً سطراً ستتعامل مع القسم كوحدة واحدة لا تتجزأ [OBSERVED].

**قاعدة هيكلية 2:** داخل القسم الواحد لا توجد أسطر حقيقية — كل التنسيق (عناوين `###`، قوائم، جداول، كتل كود، فواصل ` --- `) **مضمّن داخل سطر واحد** ويفصل بين عناصره بمسافات [OBSERVED]. استخراج الأنظمة يحتاج تقسيم السطر على `### ` و` --- ` لا على الأسطر [PROPOSED].

### ترتيب الماسترز في الملف
يطابق ترتيب أرقام المجلدات تصاعدياً (01 → 24) بلا استثناء [OBSERVED].
كل مسار مصدر يطابق اسم الماستر حرفياً: `NN_topic/Master_Name.md` [OBSERVED].
عدد المجلدات المميزة 26 لأرقام 01–24، لأن الرقم 13 مستخدم مرتين (`13_agency` و`13_agency_ops`) والرقم 17 مستخدم مرتين (`17_niche` و`17_niche_positioning`) [OBSERVED].

### جدول الماسترز الـ 39 (الترتيب كما في الملف)

| # | الماستر | مسار المصدر | §1 حروف/كلمات | §4 حروف/كلمات | §16 حروف/كلمات | الإجمالي كلمات | روابط `[[...]]` |
|---|---|---|---|---|---|---|---|
| 1 | Master_Cold_Email_System | `01_outreach/Master_Cold_Email_System.md` | 1097/184 | 5008/916 | 2359/425 | 1525 | 2 |
| 2 | Master_Email_Deliverability | `01_outreach/Master_Email_Deliverability.md` | 1524/222 | 5008/881 | 1863/324 | 1427 | 4 |
| 3 | Master_Lead_Generation | `01_outreach/Master_Lead_Generation.md` | 1584/250 | 5008/885 | 3041/531 | 1666 | 8 |
| 4 | Master_Outreach_Mechanics | `01_outreach/Master_Outreach_Mechanics.md` | 565/99 | 5008/856 | 728/130 | 1085 | 0 |
| 5 | Master_Sales_Conversation | `02_sales_closing/Master_Sales_Conversation.md` | 1114/197 | 5008/882 | 566/105 | 1184 | 0 |
| 6 | Master_High_Ticket_Closing | `02_sales_closing/Master_High_Ticket_Closing.md` | 961/161 | 5008/864 | 982/182 | 1207 | 0 |
| 7 | Master_Lead_Qualification | `02_sales_closing/Master_Lead_Qualification.md` | 1676/242 | 4962/853 | 1133/211 | 1306 | 11 |
| 8 | Master_Objection_Handling | `02_sales_closing/Master_Objection_Handling.md` | 944/168 | 5008/898 | 2134/354 | 1420 | 0 |
| 9 | Master_Pricing_And_Offer_Design | `03_pricing_offers/Master_Pricing_And_Offer_Design.md` | 1229/217 | 5008/837 | 1052/197 | 1251 | 0 |
| 10 | Master_Content_Strategy | `04_content_strategy/Master_Content_Strategy.md` | 1465/255 | 5008/859 | 5009/875 | 1989 | 0 |
| 11 | Master_Video_Production | `05_content_production/Master_Video_Production.md` | 785/146 | 2002/337 | 856/166 | 649 | 0 |
| 12 | Master_Scripting_Frameworks | `06_copywriting_scripts/Master_Scripting_Frameworks.md` | 1245/215 | 1736/294 | 1022/206 | 715 | 0 |
| 13 | Master_VSL_System | `06_copywriting_scripts/Master_VSL_System.md` | 1105/180 | 2329/398 | 1215/233 | 811 | 0 |
| 14 | Master_Storytelling_Complete | `07_storytelling/Master_Storytelling_Complete.md` | 943/158 | 1672/305 | 1217/233 | 696 | 0 |
| 15 | Master_Hooks_And_Attention | `08_hooks_attention/Master_Hooks_And_Attention.md` | 588/111 | 5008/902 | 752/147 | 1160 | 0 |
| 16 | Master_Visual_Hook_Design | `08_hooks_attention/Master_Visual_Hook_Design.md` | 510/85 | 5008/916 | 3014/552 | 1553 | 0 |
| 17 | Master_Personal_Brand_System | `09_personal_branding/Master_Personal_Brand_System.md` | 1868/323 | 5008/882 | 2100/340 | 1545 | 0 |
| 18 | Master_Brand_Authority_Positioning | `09_personal_branding/Master_Brand_Authority_Positioning.md` | 524/84 | 3278/527 | 1360/207 | 818 | 0 |
| 19 | Master_Brand_Identity_System | `09_personal_branding/Master_Brand_Identity_System.md` | 799/148 | 5008/890 | 1772/323 | 1361 | 0 |
| 20 | Master_Psychology_Influence | `10_psychology_influence/Master_Psychology_Influence.md` | 958/170 | 5008/838 | 363/72 | 1080 | 0 |
| 21 | Master_Entrepreneurship_Mindset | `11_mindset/Master_Entrepreneurship_Mindset.md` | 1016/177 | 5008/860 | 1286/230 | 1267 | 0 |
| 22 | Master_Trust_And_Authority | `12_trust_authority/Master_Trust_And_Authority.md` | 1203/212 | 5008/835 | 2322/405 | 1452 | 0 |
| 23 | Master_Agency_Scaling_Systems | `13_agency/Master_Agency_Scaling_Systems.md` | 1484/208 | 3079/462 | 764/140 | 810 | 18 |
| 24 | Master_Agency_Operations | `13_agency_ops/Master_Agency_Operations.md` | 690/131 | 5008/853 | 1332/250 | 1234 | 0 |
| 25 | Master_Business_Models | `14_business_models/Master_Business_Models.md` | 1658/275 | 5008/825 | 1182/208 | 1308 | 0 |
| 26 | Master_Digital_Products_Coaching | `14_business_models/Master_Digital_Products_Coaching.md` | 1469/204 | 3370/539 | 690/127 | 870 | 17 |
| 27 | Master_Funnel_Systems | `15_funnels_conversion/Master_Funnel_Systems.md` | 2209/371 | 5008/831 | 806/149 | 1351 | 0 |
| 28 | Master_Marketing_Strategy | `16_growth_frameworks/Master_Marketing_Strategy.md` | 1157/202 | 5008/855 | 615/110 | 1167 | 0 |
| 29 | Master_Strategic_Frameworks | `16_growth_frameworks/Master_Strategic_Frameworks.md` | 623/109 | 5008/873 | 1421/256 | 1238 | 0 |
| 30 | Master_Market_Research_Validation | `17_niche/Master_Market_Research_Validation.md` | 601/76 | 2293/379 | 489/61 | 516 | 20 |
| 31 | Master_Niche_And_Positioning | `17_niche_positioning/Master_Niche_And_Positioning.md` | 677/122 | 5008/858 | 2088/357 | 1337 | 0 |
| 32 | Master_Platform_Strategy | `18_platforms_algorithm/Master_Platform_Strategy.md` | 661/93 | 5008/748 | 562/109 | 950 | 0 |
| 33 | Master_YouTube_Strategy | `19_youtube/Master_YouTube_Strategy.md` | 776/140 | 5008/887 | 2519/442 | 1469 | 0 |
| 34 | Master_AI_And_Automation | `20_ai_automation/Master_AI_And_Automation.md` | 573/99 | 3683/544 | 1160/203 | 846 | 0 |
| 35 | Master_Metrics_And_Analytics | `21_metrics/Master_Metrics_And_Analytics.md` | 663/117 | 5008/862 | 1539/288 | 1267 | 0 |
| 36 | Master_Systems_And_Workflow | `22_systems_workflow/Master_Systems_And_Workflow.md` | 793/140 | 5008/832 | 1596/268 | 1240 | 0 |
| 37 | Master_Productivity_Deep_Work_Systems | `22_systems_workflow/Master_Productivity_Deep_Work_Systems.md` | 1138/173 | 2699/429 | 1228/217 | 819 | 6 |
| 38 | Master_Visual_Identity_Design | `23_design_visual/Master_Visual_Identity_Design.md` | 612/105 | 4752/683 | 1321/221 | 1009 | 0 |
| 39 | Master_Foundation_Business_Strategy | `24_foundation_business/Master_Foundation_Business_Strategy.md` | 692/107 | 2758/434 | 1022/185 | 726 | 9 |

أصغر ماستر: `Master_Market_Research_Validation` (516 كلمة)؛ أكبر ماستر: `Master_Content_Strategy` (1,989 كلمة)؛ الوسيط 1,234 كلمة [OBSERVED].
(ملاحظة منهجية: دراسة التباين عدّت الكلمات بطريقة مختلفة قليلاً فأعطت وسيطاً 1,236 كلمة وإجمالي 45,402 كلمة؛ الفروق ±2 كلمة ناتجة عن عدّ الترويسة والفواصل. الأرقام في هذا الجدول هي أرقام دراسة التشريح.)

## 3. الأقسام الثلاثة: التعداد والطول

كل ماستر يحتوي **الأقسام الثلاثة نفسها بالترتيب نفسه** [OBSERVED] — لا ماستر بقسم إضافي أو ناقص أو بترتيب مختلف. الأرقام 2، 3، 5–15 **غائبة تماماً** كأقسام [OBSERVED]. وجود §16 يعني أن الماستر الأصلي كان فيه 16 قسماً على الأقل، فالمضغوط يحتفظ بـ 3 منها فقط (1، 4، 16) [PROPOSED — الأصل الكامل غير موجود في هذا الأرشيف للمقارنة].

| القسم | موجود في | الترتيب | دوره الظاهري |
|---|---|---|---|
| §1 | 39/39 (100%) | الأول دائماً | الخلاصة / المقدمة |
| §4 | 39/39 (100%) | الثاني دائماً | الأنظمة الكاملة (قلب الماستر) |
| §16 | 39/39 (100%) | الثالث دائماً | الأسئلة / التطبيق / القواعد (إغلاق متعدد الأشكال) |

### الطول: min / median / max (على سطر القسم كاملاً بما فيه بادئة `**§N:** ` وعنوان `## §N…`) [OBSERVED]

| القسم | الأحرف: min | الأحرف: median | الأحرف: max | الأحرف: mean | الكلمات: min | الكلمات: median | الكلمات: max | الكلمات: mean |
|---|---|---|---|---|---|---|---|---|
| §1 | 510 | 958 | 2,209 | 1,030 | 76 | 168 | 371 | 171 |
| §4 | 1,672 | 5,008 | 5,008 | 4,329 | 294 | 853 | 916 | 734 |
| §16 | 363 | 1,217 | 5,009 | 1,448 | 61 | 217 | 875 | 257 |

**التدرّج الحجمي الثابت** [OBSERVED]:
- §4 هو القسم الأثقل في 38/39 ماستراً (الاستثناء `Master_Content_Strategy` حيث §16 أثقل: 5,009 مقابل 5,008 أحرف): حصته من حروف الماستر min 43% / median 64% / max 80%.
- §1 الأطول: `Master_Funnel_Systems` (2,209 حرفاً / 371 كلمة)؛ §1 الأقصر حروفاً: `Master_Visual_Hook_Design` (510 أحرف / 85 كلمة)، والأقصر كلماتً: `Master_Market_Research_Validation` (76 كلمة / 601 حرفاً).
- §16 الأطول: `Master_Content_Strategy` (5,009 أحرف / 875 كلمة — مقطوع بالسقف)؛ §16 الأقصر: `Master_Psychology_Influence` (363 حرفاً / 72 كلمة — جدول «بطاقة مرجع» فقط).
- §4 الأقصر غير المقطوع: `Master_Storytelling_Complete` (1,672 حرفاً / 305 كلمات) — القصر ليس دائماً أثر قطع [OBSERVED].
- تباين طول الماستر ككل: 518–1,991 كلمة (3.84×)؛ §1: 4.93×؛ §4: 3.12×؛ **§16: 14.34× — أكثر الأقسام تبايناً** [OBSERVED].

### §16: 7 أنماط وظيفية مختلفة (تصنيف يدوي بعد قراءة عناوين §16 كلها) [OBSERVED]

| النمط | العدد | أمثلة |
|---|---|---|
| أسئلة وإجابات (س:/Q:) | 15 | — |
| أسئلة مرقّمة بلا أجوبة (للتفكير/التشخيص) | 12 | `أسئلة للتفكير والتطبيق` (Outreach_Mechanics)؛ `الأسئلة العميقة (Deep Questions)` (Agency_Scaling) |
| إطار/دليل تطبيق أو checklist | 6 | `دليل التطبيق: من الصفر لأول قصة مؤثرة` (Storytelling)؛ `الخطوات العملية — البدء اليوم` (Marketing_Strategy)؛ `Implementation Checklist` (Platform_Strategy) |
| القواعد الذهبية (10 قواعد) | 2 | Lead_Qualification وVSL_System — العنوان نفسه حرفياً في الاثنين |
| أخطاء شائعة | 2 | `أخطاء كل مستوى` (Video_Production)؛ `الأخطاء الشائعة — Common Mistakes` (Brand_Authority) |
| أدوات متخصصة | 1 | `أدوات الـ Scripting المتخصصة` (Scripting_Frameworks) |
| نماذج/دراسات حالة | 1 | `نماذج حقيقية للدراسة` (Personal_Brand_System) |

- **11/39 ماستر §16 فيها صفر سؤال معدود** (رغم أن عنوان §16 أحياناً «أسئلة»): Lead_Qualification، Content_Strategy، Video_Production، Scripting_Frameworks، VSL_System، Hooks_And_Attention، Personal_Brand_System، Brand_Authority_Positioning، Psychology_Influence، Marketing_Strategy، Platform_Strategy [OBSERVED].
- إجمالي الأسئلة المعدودة في §16 (س: + مرقّمة تحتوي ؟ + Q:): 265 سؤالاً (139 بصيغة س:، 118 مرقّمة، 8 بصيغة Q:)؛ وعدد علامات ؟ في §16 كلها = 366 (370 مع 4 علامات `?` لاتينية) [OBSERVED].
- **الخلاصة:** أي أداة تفترض «§16 = أسئلة وإجابات» ستخطئ في 24/39 ماستراً [OBSERVED]. عامل §16 كقسم «إغلاق» متعدد الأشكال [PROPOSED].

### عناوين الأقسام: الرقم ثابت والعنوان نص حر [OBSERVED]
- §1 يبدأ بـ `TL;DR` في 27/39 فقط (69%)؛ الباقي: مقدمة/فلسفة/رؤية/مشكلة (10) وبلا عنوان (نقطة فقط، 2). أمثلة: `الفلسفة الأساسية: المحتوى كمحرك أعمال` (Content_Strategy)؛ `المشكلة الحقيقية: معركة الانتباه في عام 2026` (Hooks)؛ `Executive Summary` (Platform_Strategy — بالإنجليزية).
- §4 يحتوي `الأنظمة الكاملة` في 13/39؛ `الأنظمة والأساليب الكاملة` في 5؛ صيغ `الأنظمة…` أخرى في 9؛ عنوان حر لا يذكر `الأنظمة` في 10 (مثل `B-Roll Mastery: اللغة البصرية الثانية`، `الـ LATFD: الركائز الخمس للقصة الحية`، `Platform Operating Systems (40% Deep Dive)`)؛ بلا عنوان في 2.
- §16: أسئلة وإجابات بصيغها في 14/39؛ أسئلة بصيغ أخرى في 4؛ أسئلة تفكير/تطوير/تشخيص/نقدية بلا إجابات في 9؛ دليل تطبيق في 5؛ أخطاء في 2؛ القواعد الذهبية في 2؛ أدوات متخصصة/نماذج/Checklist في 3. (المجموع 39. التقسيم هنا حسب العنوان، وكل ماستر في فئة واحدة فقط: `Master_Psychology_Influence` «دليل التطبيق السريع: بطاقة المرجع» عُدَّ في دليل التطبيق، و`Master_Platform_Strategy` «Implementation Checklist» عُدَّ في أدوات/نماذج/Checklist، و`Master_Content_Strategy` «إطار التطبيق الشامل» عُدَّ في دليل التطبيق؛ تقسيم الوظيفة الفعلية في الجدول أعلاه.)

## 4. صيغ عناوين الأقسام: 5 صيغ، ثابتة داخل الماستر الواحد

سطر القسم يبدأ دائماً بالبادئة `**§N:** ` ثم عنوان Markdown `## §…` [OBSERVED]. لكن صياغة العنوان نفسه لها **5 صيغ**، وكل ماستر يلتزم بصيغة واحدة في أقسامه الثلاثة (39/39 ماستراً متسقاً داخلياً) [OBSERVED]:

| الصيغة | النمط | عدد الماسترز | مثال حرفي |
|---|---|---|---|
| A | `## §N — <عنوان>` (بلا مسافة بعد §، شرطة طويلة) | 24 | `## §1 — TL;DR (الخلاصة التنفيذية)` |
| B | `## § N: <عنوان>` (مسافة بعد §، نقطتان) | 7 | `## § 1: TL;DR — الجوهر في 60 ثانية` |
| C | `## § N — <عنوان>` (مسافة بعد §، شرطة طويلة) | 4 | `## §4 — الأنظمة الكاملة` |
| D | `## §N <عنوان>` (بلا فاصل إطلاقاً) | 2 | `## §1 TL;DR` (High_Ticket_Closing)؛ `## §1 المقدمة — Introduction` (Brand_Authority) |
| E | `## §N.` (نقطة ثم لا عنوان — العنوان مفقود) | 2 | `## §1. لماذا هذا الملف موجود…` (Lead_Qualification)؛ `## §16. القواعد الذهبية…` (VSL_System) |

الإجمالي: 72 سطر قسم بالصيغة A، 21 بالصيغة B، 12 بالصيغة C، 6 بالصيغة E (نقطة)، 6 بالصيغة D (بلا فاصل) = 117 سطراً [OBSERVED]. الصيغة A هي الغالبة (62%) لكنها ليست معياراً مطبقاً — **الضاغط لم يوحّد صيغة العنوان** [PROPOSED].
**توصية السكيل (PROPOSED):** استخدم الصيغة A دائماً في الماستر الجديد (`## §N — <عنوان>`)، والتزم بها في الأقسام الثلاثة.

## 5. الأنظمة الفرعية داخل §4 (عناوين `###`)

- إجمالي `### ` في الملف = 349 [OBSERVED]، منها 284 داخل §4 (81%)، و9 داخل §1، و56 داخل §16. و`#### ` = 78 كلها داخل §4 [OBSERVED].
- عدد `### ` داخل §4 لكل ماستر: min 2 / median 6 / max 20 / mean 7.3 [OBSERVED]. الأعلى: `Master_Psychology_Influence` (20)؛ الأدنى: `Master_Business_Models` و`Master_Funnel_Systems` (2 فقط — لأن أنظمتهما مسرودة في فقرات طويلة لا عناوين).
- أنماط عناوين `### ` داخل §4 (284 عنواناً) [OBSERVED]:
  - `4.N / §4.N` (مثل `### 4.1 نظام…` و`### §4.1 …`): 165 (58%)
  - `النظام N:` (مثل `### النظام 1: إعداد الدومين…`): 21
  - `نظام N:` (مثل `### نظام 1: Ice Breaker الجذاب…`): 9
  - `النظام الأول/الثاني…` (أرقام ترتيبية كلامية): 3
  - `نظام <اسم>` بلا رقم: 5
  - عناوين حرة أخرى (مفاهيم، مبادئ، أدوات…): 81
- **لا يوجد نمط واحد لتسمية النظام الفرعي** — الأرقام العربية (`نظام 1`) والأرقام العشرية (`4.1`) والأسماء الحرة تتعايش حتى داخل الماستر الواحد أحياناً [OBSERVED].
- **توصية السكيل (PROPOSED):** اختر نمطاً واحداً داخل الماستر (المقترح: `### 4.N <اسم النظام>`) والتزم به في كل الأنظمة.
- عناوين فرعية `### §N.M`: 63 مرة [OBSERVED] (مثل `### §4.1` و`### §16.1` و`### §1.1` — ترقيم فرعي يتبع رقم القسم الأم).

## 6. الفواصل الداخلية والتنسيق داخل القسم

| العنصر | العدد في الملف | التوزيع | الملاحظة |
|---|---|---|---|
| فاصل ` --- ` داخل سطر (لا كسطر مستقل) | 57 مرة | §4: 55، §16: 2، §1: 0 [OBSERVED] | في §4 يفصل بين الأنظمة الفرعية؛ و`---` كسطر مستقل يظهر 39 مرة فقط وهي فواصل الماسترز [OBSERVED] |
| علامة bold `**` | 3,403 مرة | §1: ~251 زوجاً، §4: ~1,109 أزواج، §16: ~341 زوجاً [OBSERVED] | التوكيد بالعريض هو أداة التنسيق الأولى؛ العناوين الصغيرة تُكتب bold بدلاً من `####` غالباً |
| عناصر مرقّمة (`1. `، `2. `…) | 763 مرة [OBSERVED] | — | القوائم المرقمة شائعة في كل الأقسام |
| عناصر نقطية (`- `) | 918 مرة [OBSERVED] | — | القوائم النقطية أكثر من المرقمة |
| كتل الكود (```) | 91 علامة فتح/إغلاق [OBSERVED] | §4: 81، §1: 8، §16: 2 | تُستخدم لقوالب جاهزة للنسخ (مثل قالب CTA في Cold_Email §4) |
| علامة الجدول `\|` | 1,408 مرة [OBSERVED] | §4: 1,181، §1: 93، §16: 134 | جداول في §4 في 29/39 ماستراً؛ وفي §1 في 3 ماسترز؛ وفي §16 في 5 ماسترز |
| اقتباس `> ` (blockquote) | 73 مرة [OBSERVED] | §4: ~40، §16: ~26، §1: ~5 | يُستخدم للقواعد الذهبية حرفياً (مثل `> لا يشتري من لا يتألم` في Lead_Qualification §16) |
| روابط Markdown `[…](…)` | 0 (صفر) [OBSERVED] | — | لا توجد روابط تشعبية Markdown في الملف إطلاقاً |
| الشرطة الطويلة ` — ` | 1,035 مرة [OBSERVED] | — | الفاصل النثري المفضل داخل الجمل |

## 7. الروابط والاستشهاد

- **روابط `[[Concept_...]]`: 95 رابطاً، 78 هدفاً مميزاً** (17 هدفاً يتكرر مرتين، والباقي مرة واحدة — لا يوجد هدف يتكرر 3 مرات أو أكثر) [OBSERVED].
- كل الروابط الـ 95 بصيغة `[[Concept_<Snake_Case>]]` بلا نص عرضي (لا `[[هدف|نص]]`) وبلا لاحقة `.md` [OBSERVED].
- التوزيع حسب القسم [OBSERVED]: §1 = 48 رابطاً، §4 = 40 رابطاً، §16 = 7 روابط (كلها في `Master_Market_Research_Validation` §16).
- التوزيع حسب الماستر [OBSERVED]: **30 من 39 ماستراً (77%) فيها صفر روابط**؛ 9 ماسترز فقط فيها روابط: Market_Research_Validation (20)، Agency_Scaling_Systems (18)، Digital_Products_Coaching (17)، Lead_Qualification (11)، Foundation_Business_Strategy (9)، Lead_Generation (8)، Productivity_Deep_Work_Systems (6)، Email_Deliverability (4)، Cold_Email_System (2). 3 ماسترز تجمع 55 من 95 رابطاً (58%).
- الموضع: **داخل الجملة** كإشارة مفاهيمية، لا في قائمة مراجع منفصلة [OBSERVED]. لا توجد قائمة «مصادر» أو «مراجع» في أي ماستر، ولا إشارات مرقمة (مثل [1]) [OBSERVED].
- **روابط خارجية (http/https): صفر** [OBSERVED]. **روابط Markdown: صفر** [OBSERVED].
- **إشارات لماسترز أخرى داخل المتن: إشارتان نثريتان في ماستر واحد** [OBSERVED]: `Master_Visual_Hook_Design` يحيل إلى `Master_Hooks_And_Attention.md` مرتين — جملة في §1 («هذا الماستر يختلف عن …») وسؤال في §16 («ما الفرق بين هذا الماستر و `Master_Hooks_And_Attention.md`؟»). وروابط ويكي `[[Master_...]]`: صفر [OBSERVED].
- إشارات لأشخاص/كتب داخل المتن (ليست روابط): أسماء مثل «محمد أسامة» و«Robert Cialdini (1984)» و«Dan Sullivan» و«Stanford Study» كنص حر بلا رابط [REPORTED — أمثلة مقيسة بالبحث النصي، لا إحصاء شامل لها؛ الإحصاء الشامل NOT_RUN].

## 8. سقف 5,000 حرف والاقتطاع الصامت

[OBSERVED — الدليل الرقمي الأقوى في الدراسة]
- 26 من 39 قسم §4 طول سطرها **5,008 أحرف بالضبط** (الوسيط = الحد الأقصى = 5,008)، وقسم §16 واحد (`Master_Content_Strategy`) طوله **5,009 أحرف بالضبط**. البادئة `**§4:** ` طولها 8 أحرف و`**§16:** ` طولها 9 أحرف — أي أن **محتوى القسم مقطوع عند 5,000 حرف بالضبط** في 27 من 117 قسماً (23.1%).
- القطع يحدث **منتصف الكلمة/الجملة** بلا علامة حذف (…) وبلا ختام [OBSERVED]. نهايات المقطوعات حرفياً:
  - Cold_Email §4: «…**قصة محمد أسامة:** - Bulk سنة كاملة: 500-2000 إيميل/يوم، 1» — ينتهي بـ `1` معلّقة.
  - Outreach_Mechanics §4: «…`### 4.4 نظام Follo`» — ينتهي منتصف كلمة «Follow».
  - Email_Deliverability §4: «…`| منتج `» — ينتهي منتصف خلية جدول.
  - Lead_Generation §4: «…ربما نطاقك واسع جداً أو المجال الذي تستهدفه غير موجود. **كيف تجد بر`» — ينتهي منتصف جملة.
  - Content_Strategy §16: «…`4 مقاييس أساسية فقط (لا Meas`» — ينتهي منتصف كلمة إنجليزية.
- **المقابل**: الأقسام غير المقطوعة (12 من §4، و38 من §1، و36 من §16) تنتهي بـ ` --- ` كخاتم قسم [OBSERVED] — غياب الخاتم علامة قطع محتملة لا معادَلة: 4 أقسام غير مقطوعة بلا خاتم (`Master_Brand_Authority_Positioning` ×3، و`Master_Visual_Hook_Design` §16) — انظر §10.2.
- **كتل كود غير مغلقة بسبب القطع** [OBSERVED]: 3 ماسترز فيها عدد فردي من ``` في §4 (High_Ticket_Closing، Pricing_And_Offer_Design، Metrics_And_Analytics) — آخر كتلة كود مفتوحة بلا إغلاق.
- **قاعدة السكيل (PROPOSED):** اكتب كل قسم أقل من 5,000 حرف محتوى (الهدف الآمن ≤ 4,800)، ولخّص ولا تقطع، واختم كل قسم بـ ` --- `.

## 9. الإحالات المعلّقة لأقسام غير موجودة

[OBSERVED] الأقسام 2، 3، 5–15 غير موجودة، لكن الضغط لم يحذف الإحالات إليها:
- 7 إحالات معلّقة: §3 (مرة)، §9 (مرتان)، §11 (مرة)، §15 (3 مرات: §15.3، §15.8، §15.11). مثال من Funnel_Systems §16: «هل نوع فنلك الحالي يطابق جدول §9؟» — والجدول §9 غير موجود في الملف.
- §16 في Objection_Handling يبدأ بـ `### §15.11 — لماذا يختلف معدل الإغلاق بين البائعين…؟` — عنوان فرعي من قسم محذوف (§15) بقي داخل §16 [REPORTED].
- إشارات § ميتة في 4 ماسترز: Funnel_Systems (§9، §15.8، §15.3)، Objection_Handling (§15.11)، Visual_Identity_Design («اطبع Checklist من §11»)، Hooks_And_Attention («من الجدول في §3.1») [OBSERVED].
- **قاعدة السكيل (PROPOSED):** لا تحل إلى أي قسم غير §1/§4/§16 في الماستر الجديد. أي إحالة داخلية يجب أن يكون هدفها موجوداً في الماستر نفسه.

## 10. الشذوذات الموثقة (لا تقلّدها)

كلها [OBSERVED] ما لم يُذكر خلاف ذلك:
1. القطع عند 5,000 حرف (23.1% من الأقسام) — انظر §8.
2. `Master_Brand_Authority_Positioning` بلا أي خاتم `---` في أقسامه الثلاثة رغم أن none منها مقطوع؛ وكذلك `Master_Visual_Hook_Design` §16 ينتهي بجملة مكتملة بلا خاتم [PROPOSED: خلل في توليد هذين الماسترين لا قاعدة].
3. عنوان مفقود (نقطة فقط): `Master_Lead_Qualification` و`Master_VSL_System` عنوان كل قسم فيهما هو `.` حرفياً (6 أسطر أقسام).
4. أقسامه §1/§4 بلا فاصل بعد الرقم: `Master_High_Ticket_Closing` و`Master_Brand_Authority_Positioning` يستخدمان `## §1 TL;DR` في الأقسام الثلاثة.
5. ماستر إنجليزي كامل تقريباً: `Master_Platform_Strategy` — §1 فيه 90.9% أحرف لاتينية من المحارف غير الفراغ (78.2% من كل المحارف؛ 100% من الحروف) و§16 عنوانه `Implementation Checklist` وقائمته checklist إنجليزية.
6. ترقيم مجلدات مكرر: `13_agency` و`13_agency_ops`، و`17_niche` و`17_niche_positioning`.
7. الربط انتقائي لا منهجي: 30/39 ماستراً بلا أي رابط، و3 ماسترز تجمع 58% من الروابط.
8. عنوان §16 «الأسئلة النقدية وخريطة الطريق» مكرر في ماسترين، لكن تشابه نص القسمين 0.173 فقط — العنوان قالب مشترك والمحتوى مختلف.
9. §4 في Lead_Qualification (4,962 حرفاً) هو الوحيد تحت السقف بفارق ضئيل وينتهي بخاتم `---`.
10. تناثر صيغ العناوين (5 صيغ) و3 أنماط لتسمية النظام الفرعي.

## 11. أرقام الجودة من دراسة التباين (للقائمة المرجعية)

- رموز النسبة `N%`: 254 في الملف؛ علامات `$`: 178؛ صفر استشهاد واحد بصيغة `path:line` أو `SRC_`؛ صفر قسم مصادر في أي ماستر [OBSERVED]. صدق الأرقام UNKNOWN.
- حرفان صينيان `除非` في عبارة واحدة في `Master_Market_Research_Validation` §4، مقابل 0 حرف صيني في الـ 38 ماستر الأخرى [OBSERVED].
- «يجب أن» 34 مرة، «دائماً» 16 مرة، «أبداً» 5 مرات في الملف [OBSERVED كعدّ؛ PROPOSED كتفسير — إشارة للمراجعة لا حكم مخالفة].
- عنوان يعد بعدد يخالفه المحتوى: `Master_Lead_Generation` §16 عنوانه «12 سؤال شائع» والمحتوى 16 سؤالاً (س1–س16)؛ وكذلك `Master_Psychology_Influence` §4 عنوانه «15 نظاماً نفسياً» والقائمة المرقّمة داخله تصل إلى 17 (الأنظمة 15–17: Confirmation Bias وHalo Effect وHindsight Bias) [OBSERVED].
- لا يوجد أي `TODO` ولا `placeholder` في الملف (0 occurrence)، ولا عناوين `###` مكررة داخل أي ماستر [OBSERVED].
- ادعاء «40%+ من المحتوى» في §4 يتحقق عددياً لكنه بلا معنى موحّد: 14 ماستراً تذكر «40%» في نصها، وحصة §4 الفعلية من الكلمات تتراوح بين 40.9% و78.7% بوسيط 64.0% [OBSERVED].

## 12. المنهج (لإعادة القياس)

```bash
F=~/workspace/release-v1.0.0/extracted/WIKI_ARCHIVE_2026-11-03/01_SDCARD_DOCS/nexus_brain_wiki_docs/NEXUS_BRAIN.md
grep -c '^## Master_' $F            # 39
wc -l -c $F                          # 434 / 421478
grep -c '^\*\*§' $F                  # 117 = 39 × 3
grep -o '\[\[[^]]*\]\]' $F | wc -l   # 95
grep -c 'https\?://' $F              # 0
```

```python
import re
txt = open(F, encoding="utf-8").read()
parts = re.split(r'^## (Master_\S+)\s*$', txt, flags=re.M)  # 39 ماستراً
# سطر القسم = سطر واحد يبدأ بـ **§N:** — الطول = len(السطر)
# السقف: len == 5008 لـ §4 (بادئة 8 أحرف) و 5009 لـ §16 (بادئة 9 أحرف) ⇒ محتوى 5000
```
