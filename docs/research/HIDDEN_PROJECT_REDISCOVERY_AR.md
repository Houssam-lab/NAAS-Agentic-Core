# إعادة اكتشاف المشروع المختبئ داخل `NAAS-Agentic-Core`

**التاريخ:** 2026-09-28  
**النوع:** Reverse engineering استراتيجي + تدقيق قدرة فعلية + بحث سوق مستقل + أطروحة منتج جديدة  
**حالة القرار:** `NEW_THESIS / UNVALIDATED_HYPOTHESIS` — لا عميل، لا عقد، لا فاتورة مدفوعة  
**النطاق:** توثيق العملة الصعبة، مسارات التعليم والدردشة الفعلية، أصول التنفيذ/التحقق، ثم مصادر سوق خارجية حديثة.

> **الحكم في جملة واحدة:** المشروع المختبئ ليس منصة تعليم مدفوعة، ولا محرك امتثال عام، ولا SaaS لمراقبة النماذج؛ بل **محرك قبولٍ قائم على الدليل للعمليات التي ينفذها وكلاء الذكاء الاصطناعي**، يبدأ كخدمة مستقلة لاختبار Workflow حقيقي قبل تسليمه إلى العميل، ويحوّل الحوار من واجهة إجابة إلى **Control Plane** لاستخراج عقد النتيجة، إزالة الغموض، تفويض التنفيذ، والتحكيم بين `ACCEPT / HOLD / UNVERIFIED` بحزمة أدلة قابلة لإعادة التشغيل.

---

# 0. طريقة البحث وحدود الصدق

## 0.1 المصادر الثلاثة

### المصدر 1 — المعرفة الاقتصادية الداخلية

أُجري مسح مستودعي على ملفات `docs/` و`studies/` و`research/` و`.memory/`. أعاد المسح 198 ملفًا مرشحًا يحتوي مصطلحات العملة الصعبة أو الإيراد أو الدفع أو العميل. لم تُعامل كل إصابة نصية كوثيقة اقتصادية؛ فُرزت المادة إلى سبع عائلات:

1. العقيدة: `FOREIGN_CURRENCY_DOCTRINE.md` و`fx_doctrine_truth.md`.
2. القيمة والإيراد: `VALUE_DOCTRINE.md` و`REVENUE_ENGINE_SPEC.md` و`revenue_engine_truth.md`.
3. دراسات السوق والعملاء: الملفات العربية الأربعة في `docs/`، و`CUSTOMER_DISCOVERY_TOP3_AR.md` و`FIRST_DEAL_ACCOUNT_RESEARCH_AR.md`.
4. عروض التصدير والكتالوج: `docs/commercial/*` و`OFFER_CATALOG.json`.
5. جولات البحث الجديدة: `docs/research/HARD_CURRENCY_NEW_KNOWLEDGE_*` و`README_NEW_KNOWLEDGE.md`.
6. بحث السوق-أولًا: `studies/market-first-sales-reality/*`.
7. أدلة القيود الجزائرية والتحصيل: `studies/dz-hard-currency-work-world/` و`research/fx-hard-currency/` وجولات القرار.

النتيجة ليست تصديق هذه الوثائق، بل **استخراج سجل فرضيات متعارضة زمنيًا**.

### المصدر 2 — الكود الفعلي

تُتبّعت نقاط الدخول والـcall chains التالية، لا أسماء المجلدات فقط:

- الواجهة: `frontend/app/components/ChatInterface.jsx`، `useAgentSocket.js`، `useRealtimeConnection.js`، و`components/generative/*`.
- حدود المحادثة: `app/api/routers/customer_chat.py` و`customer_chat_support/{turn_lifecycle,frames,pedagogy,transport}.py`.
- العميل والتوجيه: `app/infrastructure/clients/orchestrator_client.py` وحزمة `orchestrator/`.
- الرسم الفعلي: `microservices/orchestrator_service/.../graph/graph_support/_graph.py` و`graph/{state,nodes,search}.py`.
- التخطيط/البحث/الاستدلال: `skills_pipeline.py` وخدمات `planning_agent` و`research_agent` و`reasoning_agent`.
- التخصيص والقياس: `bkt_engine.py` و`bkt_persistence.py` و`tutor_state_service.py` و`concept_diagnosis_skill.py` و`semantic_property_skill.py`.
- التنفيذ: `app/services/agent_tools/*`، سياسات الأدوات، والمنفذ المسجون.
- الذاكرة: تاريخ المحادثة، Postgres checkpointer، `TutorStateService`، `memory_agent`، و`EpisodicMemoryEngine`.
- مقارنة ادعاء runtime: `.memory/runtime_truth.md` و`.memory/architecture_truth.md`.

### المصدر 3 — بحث خارجي مستقل

البحث الخارجي لم يبحث عن «فكرة startup»؛ اختبر خمسة أسئلة:

1. هل توجد عمليات AI/automation مدفوعة فعلًا؟
2. هل فشل النتائج والقبول والتتبع ألم مستقل عن بناء العملية؟
3. هل توجد ميزانية أو بدائل حالية؟
4. ما الذي أصبح سلعة رخيصة فلا ينبغي بناؤه؟
5. ما الوقائع القانونية التي تغيّرت بعد وثائق المستودع؟

## 0.2 سلم الادعاء

| الوسم | المعنى هنا |
|---|---|
| **FACT** | قابل للتحقق من الكود الحالي، سجل داخلي صريح، أو مصدر أولي خارجي. |
| **ASSUMPTION** | شرط تتصرف الوثيقة كأنه صحيح دون اختبار مباشر. |
| **HYPOTHESIS** | علاقة قابلة للاختبار بين ألم وعرض ودفع. |
| **INTERPRETATION** | قراءة تحليلية لعدة أدلة؛ ليست واقعة منفردة. |
| **UNSUPPORTED CLAIM** | ادعاء يتجاوز دليله أو أصبح قديمًا. |
| **STRATEGIC OPPORTUNITY** | تقاطع قدرة وألم يمكن اختباره، لا سوق مثبت لنا. |

## 0.3 ما لم يُثبت

- لا يوجد في المستودع `PAID_PROOF`؛ ملفات السوق نفسها تقول `GATE_C = ABSENT`.
- أسعار الغير لا تثبت استعداد أحد للدفع لنا.
- منشور «for hire» يثبت وجود عرض منافس، لا يثبت إغلاق صفقة.
- وجود كود لا يعني أنه على المسار الحي؛ ووصف `ACTIVE` في وثيقة runtime يظل لقطة زمنية تحتاج إعادة تحقق في بيئة تشغيل.
- لم تُجرَ مقابلة عميل في هذه المهمة، ولم تُرسل رسالة، ولم يُفتح حساب قبض.
- هذا التقرير ليس رأيًا قانونيًا أو مصرفيًا أو شهادة امتثال.

---

# 1. Economic Knowledge Map — ماذا تحاول وثائق العملة الصعبة تحقيقه؟

## 1.1 القصد الاقتصادي الحقيقي

الوثائق مرت بثلاثة أجيال:

1. **تعليم محلي يدفع له الطالب/الولي بالدينار:** تشخيص، اشتراك، موسم، وقسيمة.
2. **تصدير أداة أو خدمة امتثال:** فواتير فرنسا/بلجيكا، CBAM، ZATCA، EAA.
3. **تصدير قدرة تحقق/اعتمادية:** red teaming متعدد اللغات، بيانات تقييم، أدلة حوكمة، VERA/CND/AHW، ثم مسح 123 حالة بيع في 47 مجالًا.

القاسم المشترك ليس التعليم ولا الامتثال. القاسم هو:

> **تحويل معرفة أو فحص غير ملموس إلى نتيجة محدودة النطاق، قابلة للتدقيق، تُسلّم عن بعد إلى مشترٍ مؤسسي خارجي.**

هذه هي `CORE KNOWLEDGE` التي تستحق الاحتفاظ. بقية الأسماء أسواق مرشحة وليست هوية المشروع.

## 1.2 خريطة المنطق الاقتصادي

| البعد | ما تقوله المادة الداخلية فعلًا | التصنيف | الحكم |
|---|---|---|---|
| Economic Intent | دخل أجنبي قانوني ومتكرر من خدمة رقمية عالية الهامش | **STRATEGIC OPPORTUNITY** | احتفظ بالاتجاه، لا بوعد التكرار. |
| Customer Logic | انتقل من طالب/ولي إلى مكتب محاسبة، مستورد، مختبر AI، شركة أوروبية، أو وكالة أتمتة | **FACT عن الوثائق / ASSUMPTION عن السوق** | التعدد دليل بحث، لكنه يثبت غياب ICP واحد. |
| Pain Logic | الوقت، الرفض، الخطأ التنظيمي، انعدام الثقة، صعوبة التحقق، وفشل التسليم | **HYPOTHESIS** | «انعدام الثقة القابل للقياس» أقوى خيط عابر للقطاعات. |
| Value Logic | تقرير + ملف مصحح + أثر تدقيق + إعادة تشغيل + مراجعة بشرية | **STRATEGIC OPPORTUNITY** | هذه بنية قيمة قابلة للنقل. |
| Payment Logic | العميل يدفع إذا كان المخرج يقلل إعادة العمل/المخاطر/التأخير أو يفتح تسليمًا | **HYPOTHESIS** | يجب قياسه بقبول عرض مدفوع، لا بسعر منافس. |
| Delivery Logic | خدمة مُدارة أولًا، pilot محدود، ثم monitoring أو on-premise | **INTERPRETATION قوية** | احتفظ بالخدمة أولًا؛ لا تبن SaaS قبل تكرار التسليم. |
| Market Logic | السوق الدولي B2B، خصوصًا أوروبا/الخليج ومشتري AI | **ASSUMPTION واسعة** | ضيّق إلى مشترٍ واحد وسياق شراء واحد. |
| Currency Logic | عقد خدمة تصدير → فاتورة عملة أجنبية → حساب مهني → ترحيل موثق | **FACT بنيوي / تفاصيل قانونية متغيرة** | تحقق مهنيًا قبل أول عقد. |
| Evidence Logic | `PROPOSED → DISCOVERY → OFFER_READY → PILOT → PAID_PROOF → REPEATABLE` | **FACT داخلي / أصل حوكمي ممتاز** | أعد استخدامه كنظام حالة تجاري. |
| Revenue Truth | صفر عقد، صفر فاتورة، صفر دفعة حتى اللقطة | **FACT داخلي** | نقطة البداية الوحيدة الصادقة. |

## 1.3 الافتراضات الخفية

1. **أن القدرة النادرة تُباع تلقائيًا.** خطأ؛ البيع يحتاج مشتريًا، trigger، ثقة، وميزانية.
2. **أن الإلزام التنظيمي يخلق وصولًا إلى العميل.** لا؛ يخلق ألمًا فقط، وقد تلتقطه مكاتب قائمة.
3. **أن التقرير مخرج كافٍ.** العميل قد يريد إصلاحًا أو قرار قبول، لا وثيقة.
4. **أن السعر المنشور يساوي WTP لجهة جزائرية جديدة.** غير مثبت.
5. **أن وفرة الأبحاث تقلل عدم اليقين.** بعد 123 حالة سوق ما زالت `GATE_C` غائبة؛ الاختناق هو الاتصال/العرض/الدفع.
6. **أن القواعد الإضافية فقط تحافظ على المعرفة.** `additive-only` حفظ التاريخ لكنه أبقى أطروحات متناقضة حية، ورفع كلفة معرفة القرار الحالي.
7. **أن قناة التحصيل تفصيل لاحق.** هي بوابة قتل قبل الفاتورة.
8. **أن EU AI Act موعد موحد في أغسطس 2026.** أصبح هذا قديمًا جزئيًا بعد Regulation (EU) 2026/1744.

## 1.4 قرار الاحتفاظ/الاختبار/القتل/التطوير

### احتفظ

- فصل `CODE_CAPABILITY / MARKET_PROOF / LEGAL_READINESS / PAID_PROOF`.
- العرض محدود النطاق ومعيار القبول المكتوب.
- الخدمة المُدارة قبل المنصة.
- الأدلة القابلة لإعادة التشغيل بدل «ثق بنا».
- حظر ادعاء الإيراد قبل التسوية الفعلية.
- مدد دفع قصيرة ومراجعة القناة القانونية قبل الالتزام.

### اختبر

- هل وكالة أتمتة صغيرة تدفع لطرف مستقل كي يثبت النتيجة قبل handoff؟
- هل قرار `ACCEPT/HOLD` أقوى من «تقرير QA»؟
- هل packet قابل لإعادة التشغيل يقلل نزاع القبول أو ساعات إعادة العمل؟
- هل المشتري وكالة التنفيذ أم العميل النهائي؟

### اقتل الآن

- «منتج العملة الصعبة العام».
- كتالوج واسع كواجهة go-to-market.
- SaaS قبل أول ثلاث عمليات مدفوعة متشابهة.
- بيع «امتثال مضمون» أو «تجنب غرامة».
- أسعار السوق كإسقاط مباشر على سعرنا.
- جعل التعليم المنتج النهائي لمجرد أن أكبر كمية كود تعليمية.

### طوّر

- من «تقرير تدقيق» إلى **قرار قبول مدعوم بأثر تنفيذ**.
- من «اختبار نموذج» إلى **اختبار نتيجة workflow كاملة عبر حدود الأنظمة**.
- من «محادثة» إلى **مقابلة عقد نتيجة + بوابة تفويض**.
- من «ذاكرة الطالب» إلى **ذاكرة فشل/إصلاح/انحدار للعملية**.

---

# 2. Project Capability Map — ماذا يمتلك الكود فعلًا؟

## 2.1 مسار الدردشة الحي

```text
Next.js ChatInterface
  → useAgentSocket / reconnect / request_id
  → /api/chat/ws
  → JWT actor + sequential WS turn
  → local persistence + server history (حتى 50)
  → pedagogy snapshot + BKT task + tutor_state
  → OrchestratorClient
  → orchestrator-service graph / fallback paths
  → streamed text + whitelisted UI artifacts
  → deterministic close + persistence + telemetry
```

هذه ليست «نافذة chatbot» بسيطة؛ إنها قناة stateful ذات حدود أمان، بث، هوية، persistence، أحداث نهائية، وقطع UI منظمة.

## 2.2 القدرات المؤكدة ومواقعها

| القدرة | ما تفعله فعلًا | موقع الكود | الحالة الصادقة | قابلية النقل |
|---|---|---|---|---|
| محادثة متدفقة | WS، request IDs، reconnect، دمج deltas، terminal frames | `ChatInterface.jsx`, `useAgentSocket.js`, `customer_chat.py` | **موجودة ومسارها واضح** | عالية |
| سياق قصير | آخر 30 رسالة من العميل + حتى 50 من الخادم، ودمج منضبط | `useAgentSocket.js`, `frames.py`, `turn_lifecycle.py` | **موجود** | عالية |
| حالة دائمة | conversation persistence، Postgres checkpointer، `tutor_state` | boundary service، graph compile، `TutorStateService` | **متعددة المستويات** | عالية بعد توحيد الملكية |
| كشف النية | حراس حتمية + DSPy + fallback heuristics | `SupervisorNode`, `intent_detector.py` | **موجود، لكنه domain-heavy** | متوسطة |
| استرجاع/بحث | KB محلي، reranking، web fallback، research-agent | graph search + research service | **موجود؛ تفعيله بيئي** | عالية |
| تخطيط | planning-agent يولد plan/critique | `microservices/planning_agent/*` | **موجود** | عالية |
| استدلال | reasoning-agent وMCTS/LLM | `microservices/reasoning_agent/*` | **موجود، الجودة غير مثبتة تجاريًا** | متوسطة |
| تنفيذ أدوات | registry، schema validation، policy، file/git/test/shell | `app/services/agent_tools/*` | **موجود داخل سجن المشروع** | متوسطة؛ لا موصلات أعمال |
| مراجعة/تحقق | validator node، reviewer، output firewall، symbolic checks لبعض الرياضيات | graph + skills | **موجود لكن متفاوت الصرامة** | عالية كمبدأ، منخفضة كـbusiness verifier جاهز |
| تشخيص | concept/misconception، probe قبل intervention | `concept_diagnosis_skill.py`, `semantic_property_skill.py` | **موجود للتعليم/الاحتمالات** | الآلية عالية، المعرفة منخفضة |
| تكيّف | support level، policy per turn، anti-loop | `pedagogical_policy_engine.py`, `TutorStateService` | **موجود** | عالية بعد إعادة تسمية الحالة |
| قياس تقدّم | BKT assisted/durable، illusion gap، append-only evidence | `bkt_engine.py`, `bkt_persistence.py` | **موجود وحتمي جزئيًا** | عالية كـevidence-strength primitive، لا كـBKT تجاري مباشر |
| artifacts | بطاقات UI ذات whitelist، Markdown/KaTeX، ملفات وتقارير مهام | Generative UI + mission/file tools | **موجود** | عالية |
| ملاحظة وتشغيل | Prometheus، traces، correlation IDs، service health | observability + service metrics | **واسع** | عالية |
| حوكمة الادعاء | truth tables، fitness gates، evidence ledgers | `.memory`, `scripts/fitness`, commercial states | **أصل غير اعتيادي** | عالية جدًا |

## 2.3 Educational Features مقابل General Intelligence Primitives

| Educational Feature | Primitive المستخرج | ما لا ينتقل تلقائيًا |
|---|---|---|
| تشخيص مفهوم رياضي | كشف فجوة/غموض + سؤال probe قبل القرار | قاموس المفاهيم الرياضي وإشارات الأخطاء |
| BKT للإتقان | تحديث belief من evidence متتابع + فصل assisted عن durable | معادلات BKT لا تثبت صلاحيتها لقياس workflow reliability |
| support level | سلّم استقلال/مساعدة للقرار | معنى «الدعم 1..5» التربوي |
| منع كشف الإجابة | policy gate قبل إجراء عالي الأثر | قواعد حجب النتائج الرياضية |
| tutor state | state machine طويلة العمر مع anti-loop | حقول concept/learning stage الحالية |
| knowledge graph للمنهاج | graph dependencies + root-cause traversal | عقد المنهاج وحوافه |
| بطاقات الاحتمالات | typed artifact rendering | المكونات المرئية الرياضية نفسها |
| Socratic tutor | ambiguity-reduction dialogue | نبرة المعلم وهدف التعلم |
| مراجعة الإجابة | evaluator + acceptance gate | rubric التعليمية الحالية |
| التكرار المتباعد | schedule retest after change/time | FSRS لا يُنقل بلا تحقق إلى صيانة البرامج |

## 2.4 قيود تمنع المبالغة

1. `skills_pipeline.py` يصف مسارًا يعتمد فيه البحث على الخطة والاستدلال على الاثنين، لكن التنفيذ الحالي يستدعي الثلاثة بالتوازي مع `context=""`. ثم `_compose_answer` يركب النصوص ويشتق الثقة أساسًا من عدد الخدمات الناجحة. **هذه ليست سلسلة Plan→Research→Reason→Verify.**
2. `EpisodicMemoryEngine` موجود، لكن الوجود وحده لا يثبت استعماله على المسار الحي؛ أما تاريخ المحادثة و`tutor_state` وcheckpointer فهي أوضح اتصالًا.
3. منفذ الأدوات آمن نسبيًا داخل جذر المشروع، لكنه لا يستطيع اليوم اختبار CRM أو بريد أو تقويم عميل.
4. `OutputFirewall` fail-open في حالات؛ لا يصلح وحده بوابة قبول اقتصادية.
5. الـGenerative UI غني لكنه educational registry؛ نحتاج artifacts أعمال جديدة.
6. خدمات كثيرة موصوفة `ACTIVE` في snapshot داخلي، لكن الجاهزية تعتمد على مفاتيح وعمليات وخدمات خارجية. يجب إعادة إثباتها في بيئة التسليم.
7. لا توجد كيانات engagement، outcome contract، scenario، run evidence، acceptance verdict، أو invoice settlement.

---

# 3. DNA المشروع

```text
EXISTING DOCUMENTATION
  ├─ قيمة محدودة النطاق
  ├─ عميل مؤسسي خارجي
  ├─ دليل قبل الادعاء
  ├─ خدمة مُدارة قبل المنتج
  ├─ قبول/بوابات/حالة نضج
  └─ دفع قانوني موثق
                 ↓
        CORE ECONOMIC KNOWLEDGE

EXISTING EDUCATIONAL CODE
  ├─ Conversation + Context + State
  ├─ Probe-before-intervention
  ├─ Planning + Research + Reasoning
  ├─ Tool execution + policy
  ├─ Evaluation + verification
  ├─ Persistent evidence over turns
  ├─ Human-readable artifacts
  └─ Telemetry + governance
                 ↓
          CORE CAPABILITIES

CORE ECONOMIC KNOWLEDGE + CORE CAPABILITIES
                 ↓
SEARCH SPACE: systems that convert ambiguous intent into a verified,
accepted, remotely deliverable business outcome
```

**التقاطع الخفي:** ما بنته المنظومة للتأكد من أن «الطالب فهم فعلًا، لا أنه بدا فاهمًا تحت المساعدة» يمكن إعادة صياغته للتأكد من أن «الـworkflow أنتج نتيجة العمل فعلًا، لا أن لوحة التنفيذ أصبحت خضراء».

هذا ليس نقل BKT إلى الأعمال حرفيًا. إنه نقل **البنية المعرفية**:

```text
apparent success ≠ durable verified success
```

إلى:

```text
successful run ≠ correct downstream business outcome
```

---

# 4. Contradiction Map

| التناقض | الدليل الداخلي/الخارجي | الأثر | القرار |
|---|---|---|---|
| التعليم هو الأصل الأكبر، لكن العملة الصعبة انتقلت إلى الامتثال/AI | codebase مقابل commercial corpus | هوية مشوشة | افصل القدرة عن المجال. |
| 7 خطوط عرض في الكتالوج، ثم D-296 ألغى الحصر | `OFFER_CATALOG.json` | لا ICP واحد | الكتالوج بحث، لا go-to-market. |
| «خطط ثم ابحث ثم استدل» مقابل parallel empty context | `skills_pipeline.py:502-505` | ثقة تركيب غير سببية | صمّم DAG جديدًا متسلسلًا للقبول. |
| وثائق runtime القديمة تصف أجزاء dormant، وأخرى لاحقة تصفها active | `.memory/architecture_truth.md` مقابل `.memory/runtime_truth.md` | snapshot drift | تحقق حي قبل reuse. |
| «ذاكرة عميقة» مقابل تعدد مخازن وحالات | history/checkpointer/tutor_state/memory_agent/episodic | ownership غامض | engagement state واحد وevidence ledger append-only. |
| حوكمة صارمة مقابل fail-open في بعض firewalls | code | مناسب للتعليم، لا للقبول المالي | fail-closed فقط عند verdict؛ fail-open للشرح. |
| سعر المنافس/السوق مقابل صفر paid proof لنا | كل الدراسات التجارية | وهم قابلية البيع | لا سعر نهائي قبل pilot مدفوع. |
| إضافة فقط تحفظ المعرفة، لكنها تمنع قتل الفرضية في النص الأصلي | الدساتير وجولات التصحيح | corpus متضخم ومتناقض | سجل supersession صريح؛ لا حذف الأدلة، لكن اقتل القرار. |
| وثائق قديمة تعامل 2 أغسطس 2026 كموعد high-risk | corpus السوقي | urgency غير صحيحة | Regulation 2026/1744 يؤجل Annex III إلى 2 ديسمبر 2027 وAnnex I إلى 2 أغسطس 2028 [1](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng). |
| الامتثال يبدو أقرب مالًا، لكنه يحتاج ثقة قانونية وخبيرًا | internal offers | liability مرتفعة | لا تبدأ به؛ استخدمه لاحقًا كmapping للأدلة لا كشهادة. |
| red teaming له ميزانيات كبيرة، لكن لا سجل أمني تجاري | code + offers | credibility gap | لا تبدأ بخطاب pentest؛ ابدأ acceptance assurance محدودًا. |

---

# 5. External Market Discovery

## 5.1 أين الإنفاق الحقيقي؟

### أ. بناء الأتمتة والوكلاء مدفوع بالفعل

مزودون ينشرون نطاقات من مئات الدولارات لعملية بسيطة إلى آلاف/عشرات آلاف للأنظمة، وعقود صيانة شهرية؛ هذه **أدلة على تسعير الموردين لا على صفقاتنا**. مثال منشور لوكالة يضع multi-workflow AI عند `$1.5K–$4.5K` وعقود الرعاية `$1.2K–$8K/month` [1](https://buldrr.com/n8n-automation-agency-pricing/)، ومصدر آخر يضع مشاريع n8n الوكالية من `$5K` إلى `$50K+` حسب التعقيد [6](https://goodspeed.studio/blog/n8n-pricing).

**المعنى:** توجد قيمة اقتصادية محيطة بالـworkflow تكفي نظريًا لاقتطاع ميزانية قبول/QA، لكن الاقتطاع نفسه ما زال فرضية.

### ب. الألم ليس «النموذج سيئ» فقط، بل انفصال الاختبار عن التنفيذ

مسح Inngest لـ130 مهندسًا وجد أن 68% يبنون AI workflows في الإنتاج، و74% من فرق AI شهدت حادثة ظاهرة للعميل خلال 90 يومًا. والأهم أن 47% ذكروا فجوات سياق مثل: نتائج eval في نظام منفصل، لا طريقة للتصرف بعد الفشل، coverage غير موثوق، أو eval منفصل عن سلوك الإنتاج [8](https://www.inngest.com/blog/ai-in-production-report-2026).

مسح Cleanlab لقادة لديهم AI في الإنتاج وجد أن أقل من ثلث الفرق راضٍ عن observability والguardrails، وأن reliability أضعف طبقة [4](https://cleanlab.ai/ai-agents-in-production-2025/).

**المعنى:** السوق لا يحتاج dashboard إضافيًا بقدر ما يحتاج ربط: failure → decision → action → retest → evidence.

### ج. الأمن والتدقيق بوابات شراء، لكن البيع المباشر للمؤسسة ليس إسفيننا الأول

KPMG يذكر أن 75% من قادة عينة مؤسسات كبيرة أعطوا الأمن والامتثال وقابلية التدقيق أولوية في نشر الوكلاء، و80% عدّوا الأمن السيبراني أكبر حاجز [2](https://kpmg.com/us/en/media/news/q4-ai-pulse.html). Okta وجدت أن 69% يقولون إن مخاوف الأمن تبطئ تبني الوكلاء، مع أولوية لتسرب البيانات والصلاحيات الزائدة [4](https://www.okta.com/newsroom/articles/enterprise-buyer-survey-ai-agent-security/).

**الحد:** هذه عينات enterprise ولا تثبت أن شركة صغيرة ستشتري منا مباشرة. لكنها تفسر لماذا تحتاج الوكالة التي تبيع إلى enterprise دليلًا أفضل عند handoff.

### د. المنصات الحالية تجعل «observability/evals SaaS» سوقًا مزدحمًا ورخيص الدخول

LangSmith يعرض free tier ثم `$39/seat/month`، وBraintrust free ثم Pro منشورًا عند `$249/month` [3](https://www.langchain.com/resources/llm-observability-tools). توجد بدائل مفتوحة المصدر وذاتية الاستضافة كذلك [6](https://laminar.sh/article/langsmith-alternatives-2026).

**النتيجة:** بناء clone عام للتتبع/evals قرار سيئ. الفرصة فوق الأدوات: **تحويل business intent إلى acceptance contract، وتشغيل تحقق downstream، وإصدار verdict يفهمه البائع والمشتري.**

### هـ. قبول workflow كفئة موجود لكنه غير مثبت النضج

يوجد عرض علني مستقل لاختبار n8n: 5 سيناريوهات و`ACCEPT/HOLD/UNVERIFIED` بسعر `$149`، مع تحقق من النتيجة downstream لا مجرد execution green [3](https://community.n8n.io/t/for-hire-independent-acceptance-test-for-one-critical-n8n-workflow-5-scenarios-149-fixed/311749). وتوجد عروض QA أوسع توثّق expected/actual/severity/reproduction/evidence [1](https://community.n8n.io/t/for-hire-independent-qa-testing-for-n8n-workflows-ai-agents/315718).

**التصنيف الصحيح:**

- وجود المنافس/العرض: **FACT**.
- وجود category language: **FACT ضعيف**.
- وجود طلب متكرر وميزانية مستقلة: **UNVALIDATED HYPOTHESIS**؛ المنشورات لا تثبت الدفع.

### و. best practice تؤكد فجوة failure paths

إرشادات إنتاج n8n توصي باختبار malformed inputs، credentials منتهية، API timeouts، empty results، versioning، rollback، ومراجعة ثانية للعمليات عالية الأثر [4](https://hatchworks.com/blog/ai-agents/n8n-best-practices/). OWASP Agentic يركز على least agency، موافقات بشرية، سجلات غير قابلة للتلاعب، وعزل الذاكرة والسياق [3](https://vamisec.com/en/wissen/agentic-ai-security/owasp-agentic-top-10).

**المعنى:** scenario library الأول يمكن أن يبدأ من failure modes معروفة، لكن pass/fail يجب أن يرتبط بعقد نتيجة العميل لا checklist عام.

## 5.2 تصحيح قانوني جديد يجب أن يدخل معرفة المشروع

المصدر الرسمي الأوروبي الحالي يقول:

- تطبيق قواعد Annex III high-risk: **2 ديسمبر 2027**.
- AI المدمج في منتجات Annex I: **2 أغسطس 2028**.
- دخل AI Omnibus حيز التنفيذ في 27 يوليو 2026 [2](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) و[3](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202601744).
- بعض التزامات الشفافية والحوكمة والتنفيذ بدأت في أغسطس 2026، فلا يعني التأجيل اختفاء السوق [5](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence).

**المعرفة الجديدة:** لا نبني عرضنا الأول على «هلع موعد أغسطس 2026». التأجيل يضعف urgency القصيرة لخدمة high-risk compliance، لكنه يمنح نافذة لبناء evidence operations. هذا سبب إضافي لاختيار workflow acceptance أولًا.

---

# 6. Capability-to-Market Map

| Capability في الكود | مجالها الحالي | هل تُعمم؟ | السوق/الوظيفة المحتملة | القيمة المحتملة | الحكم |
|---|---|---:|---|---|---|
| الحوار | تعليم | نعم | discovery + acceptance interview | تحويل الكلام إلى شروط قابلة للاختبار | **REUSE** |
| التشخيص + probes | مفهوم خاطئ | نعم بالآلية | كشف غموض outcome/exception policy | منع اختبار المتطلب الخطأ | **ADAPT** |
| السياق والحالة | جلسة طالب | نعم | engagement/workflow state | استمرارية قرار القبول | **REUSE/REDESIGN** |
| support ladder | مقدار مساعدة | جزئيًا | evidence strength ladder | فصل success assisted عن autonomous | **RESEARCH**؛ لا تنقل المعادلة |
| BKT append-only | mastery | جزئيًا | reliability evidence history | قياس تغير الثقة عبر retests | **ADAPT DATA MODEL ONLY** |
| planner | خطة تعلم/مهمة | نعم | scenario plan | coverage bounded | **REUSE** |
| research | محتوى/ويب | نعم | docs/API/failure-mode research | test enrichment with sources | **REUSE** |
| reasoning | حل | جزئيًا | candidate assertions / edge cases | تسريع authoring | **REUSE كاقتراح لا oracle** |
| tools/sandbox | ملفات/كود | نعم جزئيًا | test harness/artifact generation | تنفيذ قابل للتكرار | **REUSE + NEW CONNECTORS** |
| validator/reviewer | جودة إجابة | نعم كمبدأ | deterministic oracle + human review | verdict موثوق | **REDESIGN** |
| generative UI | تعليم بصري | نعم للبنية | contract/scenario/run/verdict cards | تقليل الغموض والموافقة | **REUSE SHELL, BUILD CARDS** |
| memory | تعلم الطالب | نعم بحذر | incident→regression memory | كل فشل يصبح اختبارًا دائمًا | **CONSOLIDATE** |
| telemetry | تشغيل النظام | نعم | run evidence/correlation | traceability | **REUSE** |
| governance gates | صدق الادعاء | نعم جدًا | evidence maturity and claim bounds | ثقة المشتري | **REUSE CORE** |
| HCE validators | امتثال محدد | ليس عامًا | plugins مستقبلية | oracles domain-specific | **KEEP OUT OF MVP CORE** |

---

# 7. New Knowledge — المعرفة التي لم تكن موجودة بهذه الصياغة

## NK-1 — «فجوة الوهم» الاقتصادية ليست بين ثقة الطالب وإتقانه؛ بل بين run أخضر ونتيجة صحيحة

المشروع يملك من التعليم مبدأ فصل النجاح المدعوم عن الإتقان الدائم. السوق الخارجي يكشف أن فرق الإنتاج ترى logs/evals لكنها تظل غير قادرة على التصرف أو إثبات النتيجة. إذن الأصل القابل للبيع ليس BKT، بل **نظام يفصل الإشارة السطحية عن النتيجة الاقتصادية downstream**.

## NK-2 — أقرب مشترٍ ليس المؤسسة التي تحتاج governance، بل البائع الذي يحتاج قبولًا كي يُغلق التسليم

بيع AI governance مباشرة إلى enterprise يتطلب علامة وثقة ودورة مشتريات. وكالة الأتمتة الصغيرة لديها بالفعل:

- عميل قائم.
- workflow قائم.
- موعد handoff.
- دفعة نهائية أو سمعة على المحك.

إذن trigger الشراء أقرب: **قبل التسليم/بعد فشل/قبل retainer renewal**.

## NK-3 — الدردشة ليست channel support؛ إنها compiler لعقد النتيجة

المتطلبات التجارية تصل غامضة: «إذا كان lead جيدًا، أضفه واتصل به». الحوار التشخيصي الموجود يمكن أن يسأل حتى تصبح العبارة:

```text
Given lead with consent + score ≥ threshold
When webhook received once
Then exactly one CRM contact is created,
owner is assigned, notification is sent within T,
and retry creates no duplicate.
```

قيمة الدردشة هنا هي **خفض entropy قبل التنفيذ**، لا الإجابة.

## NK-4 — الـartifact المدفوع ليس report بل Evidence-backed Acceptance Decision

البدائل الرخيصة تنتج traces أو dashboards. المشتري يحتاج قرارًا قابلًا للتصرف:

- `ACCEPT`: كل assertions الحرجة مرّت بأدلة كافية.
- `HOLD`: فشل حرج قابل لإعادة الإنتاج.
- `UNVERIFIED`: لم يسمح الوصول أو لا يوجد oracle كافٍ.

`UNVERIFIED` مهم اقتصاديًا: يمنع confidence زائفًا ويحدد ما يجب شراؤه/إتاحته لإغلاق القبول.

## NK-5 — ذاكرة الفشل أقوى من ذاكرة المحادثة

القيمة المتكررة لا تأتي من «تذكّر العميل»؛ تأتي من:

```text
incident → minimized scenario → regression test → retest after change
```

كل حادثة تزيد أصول القبول للوكالة عبر عملائها، فتنتقل الخدمة من one-off إلى assurance retainer.

## NK-6 — التنظيم ليس المنتج الأول، بل schema mapping لاحق للأدلة نفسها

عندما يصبح لكل run provenance، approval، tool calls، expected/actual، human override، وversion، يمكن لاحقًا mapping إلى NIST/OWASP/EU evidence. لا نبيع certification؛ نعيد استخدام الأدلة التشغيلية. بذلك يأتي الامتثال **كناتج ثانوي للدليل الحقيقي** لا كقالب وثيقة فارغ.

## NK-7 — التنفيذ المتوازي الحالي مناسب لجمع آراء، لا لإصدار verdict

القبول يحتاج dependencies صريحة:

```text
contract → scenarios → authorization → execute → verify → review → verdict
```

لا يجوز أن يعمل verifier بلا contract أو reasoning بلا evidence. لذلك المنتج الجديد يحتاج graph جديدًا صغيرًا، لا إعادة تسمية `skills_pipeline`.

---

# 8. New Strategic Thesis

## الأطروحة

> **نحوّل CogniForge من معلّم يختبر الفهم إلى طرف قبول مستقل يختبر أن وكيل/أتمتة AI حقق نتيجة العمل الصحيحة تحت الحالات العادية والفشل، ثم يصدر قرارًا وحزمة أدلة قابلة لإعادة التشغيل تساعد وكالة التنفيذ على تسليم المشروع، تحصيل الدفعة النهائية، والاحتفاظ بعقد الصيانة.**

## العميل الأول

**وكالات/استوديوهات أتمتة صغيرة تبني n8n/Make/custom AI workflows لعملاء خارجيين، ولا تملك وظيفة QA/eval مستقلة.**

- المستخدم: builder أو automation engineer.
- champion: owner/technical lead.
- المشتري: owner/delivery lead.
- المستفيد الثاني: عميل الوكالة الذي يوقّع القبول.
- trigger: 3–7 أيام قبل handoff، فشل سابق، نزاع scope، أو renewal.

## ما لا ندعيه

- لا نضمن أن السوق سيدفع؛ الحالة `UNVALIDATED HYPOTHESIS`.
- لا نقوم pentest أو legal certification.
- لا نضمن zero incidents.
- لا نصل الإنتاج أو ننفذ mutation بلا تفويض صريح.
- لا نستبدل LangSmith/Braintrust/n8n logs؛ نستهلك ما يلزم ونضيف طبقة outcome acceptance.

---

# 9. New Product Definition

## الاسم الوظيفي

**Outcome Assurance Engine (OAE)**  
**العربية:** محرك قبول النتائج للعمليات الوكيلة.

## المنتج الحقيقي

ليس SaaS عامًا. يبدأ كـ**خدمة مُدارة مدعومة بآلة داخلية**:

> `Workflow Acceptance Sprint` لعملية AI واحدة حرجة، من عقد النتيجة إلى تنفيذ السيناريوهات والتحقق downstream وقرار القبول وإعادة اختبار واحدة.

## المدخلات

- workflow export أو staging endpoint.
- وصف النتيجة التجارية.
- sample/sanitized payloads.
- قائمة الأنظمة downstream وصلاحيات read-only حيث أمكن.
- exception policy والآثار المحظورة.
- versions: workflow/model/prompt/config.

## المخرجات

1. Outcome Contract موقّع/موافق عليه.
2. Scenario Pack محدود ومرقّم.
3. Run Ledger بمدخلات منزوعة الحساسية وhash/version/timestamps.
4. Expected vs Actual لكل assertion.
5. Failure taxonomy + severity + reproduction.
6. `ACCEPT / HOLD / UNVERIFIED` مع سبب.
7. Remediation brief.
8. Retest delta.
9. Regression pack قابل لإعادة التشغيل.

## لماذا يدفع العميل؟

ليس لامتلاك chatbot أو dashboard، بل لأن المخرج يمكن أن:

- يقلل ambiguity ونزاع القبول.
- يكشف partial success قبل العميل النهائي.
- يجعل الفشل reproducible بدل «حدث مرة».
- يحول incident إلى regression asset.
- يدعم تحصيل مرحلة التسليم أو renewal — **هذه علاقة سببية يجب قياسها في pilot، لا افتراضها.**

---

# 10. New Conversational Role

واجهة الدردشة تصبح **Evidence & Authorization Console** بأربع وظائف فقط:

1. **Outcome Interviewer:** تستخرج النتيجة، القيود، الاستثناءات، والآثار المحظورة.
2. **Ambiguity Resolver:** تسأل probe واحدًا في كل مرة حتى يصبح الشرط قابلًا للاختبار.
3. **Execution Gate:** تعرض ماذا سيُنفذ وبأي بيانات وأي صلاحيات، وتطلب موافقة صريحة.
4. **Decision Explainer:** تشرح لماذا `HOLD` أو `UNVERIFIED` وترتبط بكل ادعاء بدليله.

الدردشة **ليست**:

- oracle للقبول.
- مكانًا لإخفاء tool actions.
- بديلًا عن artifact.
- قناة لإعطاء موافقة عامة على إجراءات production.

أفضل انتقال للحالات:

```text
AMBIGUOUS_NEED
  → OUTCOME_CONTRACT_DRAFT
  → CONTRACT_CONFIRMED
  → SCENARIOS_APPROVED
  → ACCESS_AUTHORIZED
  → RUNNING
  → EVIDENCE_INCOMPLETE | FAILURES_FOUND | VERIFIED
  → HOLD | UNVERIFIED | ACCEPT
  → RETEST
  → REGRESSION_BASELINE
```

---

# 11. New Economic Engine

## 11.1 Revenue Feature مقابل Economic Engine

| Revenue Feature | Economic Engine |
|---|---|
| زر دفع | نتيجة قبول تقلل مخاطرة التسليم |
| اشتراك dashboard | كل فشل يتحول إلى regression asset |
| tokens/seat | fixed-scope workflow + acceptance criteria |
| report مولد | evidence from actual execution + downstream verification |
| «AI-powered» | verdict قابل للطعن وإعادة التشغيل |

## 11.2 الحلقة الاقتصادية

```text
Agency has a workflow near handoff
→ conversation compiles business outcome
→ scoped quote + deposit
→ authorized staging access
→ scenarios generated and approved
→ workflow executed
→ downstream outcome independently verified
→ evidence packet + verdict
→ agency fixes failures
→ one retest
→ final acceptance packet
→ agency closes handoff / reduces rework
→ our final invoice settles in EUR/USD
→ incident scenarios enter regression library
→ optional monthly change/retest contract
```

## 11.3 وحدة القيمة ووحدة السعر

- **وحدة القيمة:** workflow واحد + outcome contract واحد + عدد محدود من السيناريوهات + retest واحد.
- **ليست الوحدة:** token، trace، كلمة، أو ساعة غير محدودة.
- **سعر أول pilot:** فرضية تُختبر، لا حقيقة سوق.
- **التكرار:** retest عند تغيير model/prompt/workflow/API، لا اشتراك مصطنع.

## 11.4 العملة الصعبة

لا تتحقق حتى تكتمل السلسلة:

```text
foreign buyer
→ signed scope
→ lawful service invoice
→ payment to eligible professional FX rail
→ bank/accounting evidence
→ delivery acceptance
→ recognized net margin
```

أي proposal أو invoice غير مسوّاة يبقى دون `PAID_PROOF`.

---

# 12. New Architecture

## 12.1 مبدأ التصميم

ابنِ **vertical slice واحدًا داخل modular monolith** قبل microservice جديد. لا ننشئ 12 خدمة لأن المستودع يملك خدمات كثيرة؛ حدود جديدة لا تُبرر إلا عند وجود حمل/ملكية/عزل مستقل.

## 12.2 المكونات

| Component | Purpose | Input | Output | Dependency | Business Value | Technical Justification |
|---|---|---|---|---|---|---|
| Assurance Chat Adapter | إعادة استخدام UI/WS لحوار engagement | messages + engagement_id | commands/events | chat transport | وقت بناء أقل | البروتوكول والبث موجودان |
| Engagement State Store | SSOT للحالة التجارية والتنفيذية | state transitions | current state + history | Postgres | لا ضياع/تناقض | لا تستخدم tutor_state بأسماء تربوية |
| Outcome Contract Compiler | تحويل اللغة إلى assertions | dialogue + examples | typed contract | probes + schema | يمنع اختبار المطلوب الخطأ | adaptation للتشخيص لا prompt واحد |
| Scenario Planner | بناء حالات bounded | contract + failure library | scenario set | planner/research | coverage واضحة | sequential dependency |
| Authorization Gate | ضبط البيئة والصلاحيات | scenario actions | signed approval scope | RBAC/policy | يمنع ضررًا وثقة أعلى | fail-closed للـmutations |
| Connector Adapter | تشغيل workflow وقراءة downstream | endpoint/export/credentials | normalized events | HTTP + n8n first | يجعل الاختبار حقيقيًا | ابدأ بموصل واحد |
| Scenario Runner | تنفيذ مع idempotency/timeouts | approved scenarios | run records | connector | reproducibility | state machine صغيرة |
| Deterministic Verifier | فحص schema/count/state/timing | expected + observed | assertion results | read-only probes | verdict موثوق | LLM لا يقرر pass منفردًا |
| Human Review Queue | تحكيم الحالات غير الحتمية | evidence bundle | reviewed result | reviewer | يحد false confidence | البشر للحالات الدلالية فقط |
| Evidence Ledger | provenance append-only | every transition/run | hashed bundle | storage | portable trust | مستلهم من الحوكمة الحالية |
| Verdict Engine | إصدار ACCEPT/HOLD/UNVERIFIED | assertion results | bounded verdict | policy | قرار قابل للتصرف | rules لا prose حر |
| Artifact Builder | report JSON/MD/PDF لاحقًا | ledger + verdict | acceptance packet | existing artifact shell | deliverable مدفوع | ابدأ MD+JSON، لا PDF engine |
| Regression Memory | حفظ أصغر فشل كاختبار | incident/fix/retest | reusable scenario | ledger | recurring value | ليس chat memory عامًا |
| Economic Event Ledger | ربط quote/deposit/delivery/settlement | commercial events | proof state | manual first | يمنع revenue fiction | لا يلزم Stripe في MVP |

## 12.3 تدفق التنفيذ

```text
Chat Intake
   ↓
Outcome Contract Compiler ──(ambiguity?)──→ Probe Loop
   ↓ confirmed
Scenario Planner
   ↓ approved
Authorization Gate
   ↓
Connector → Scenario Runner → Raw Evidence Ledger
                              ↓
                    Deterministic Verifier
                              ↓ uncertain only
                       Human Review Queue
                              ↓
                         Verdict Engine
                              ↓
                 Acceptance Packet + Retest
                              ↓
                       Regression Memory
```

## 12.4 عقود البيانات الدنيا

```python
OutcomeContract(
    actor, trigger, preconditions, expected_effects,
    forbidden_effects, timing_bounds, idempotency_rules,
    evidence_sources, approved_environment, version
)

Scenario(
    id, setup, input_fixture, expected_assertions,
    allowed_actions, cleanup, severity_if_failed
)

RunEvidence(
    scenario_id, started_at, versions, input_hash,
    tool_events, observed_outputs, downstream_probes,
    redactions, verifier_results
)

Verdict(
    status="ACCEPT|HOLD|UNVERIFIED",
    scope, critical_failures, unverifiable_claims,
    evidence_refs, issued_at, reviewer
)
```

## 12.5 قرارات هندسية إلزامية

- لا production mutation في MVP؛ staging أو dry-run أو synthetic data.
- credentials قصيرة العمر وread-only حيث أمكن؛ لا تُحفظ في chat history.
- كل action له correlation ID وidempotency key.
- LLM يقترح scenarios ويشرح؛ deterministic assertions أو reviewer يقرران.
- `UNVERIFIED` ليس فشلًا تقنيًا بل مخرج من الدرجة الأولى.
- graph جديد 7–9 عقد، لا تلوين graph التعليمي بأسماء أعمال.
- لا microservice ولا vector DB جديد في MVP.

---

# 13. Reuse / Redesign / Delete / Build Matrix

| الأصل | القرار | السبب |
|---|---|---|
| WebSocket transport, request IDs, terminal event discipline | **REUSE** | بنية production مكلفة أُنجزت. |
| Chat shell + Markdown | **REUSE** | واجهة intake/explanation مناسبة. |
| Generative UI registry | **REDESIGN** | أضف contract/scenario/run/verdict cards؛ لا تحمل بطاقات الرياضيات. |
| Auth/RBAC/persistence | **REUSE** | أساس الهوية والملكية. |
| Postgres checkpointer | **REUSE** | استمرارية graph، مع engagement namespace. |
| TutorState schema | **DO NOT REUSE AS-IS** | domain leakage؛ استخرج pattern فقط. |
| Concept diagnosis/probe policy | **REDESIGN** | حوّل taxonomy إلى outcome ambiguity taxonomy. |
| BKT math | **KEEP EDUCATIONAL ONLY** | لا صلاحية مثبتة للـworkflow. |
| assisted/durable distinction | **RESEARCH/ADAPT** | يتحول إلى evidence-strength، لا معادلة BKT. |
| planning/research/reasoning clients | **REUSE SELECTIVELY** | adapters مفيدة؛ orchestration الحالي غير مناسب. |
| parallel `skills_pipeline` as acceptance engine | **DELETE FROM NEW CALL CHAIN** | يكسر dependencies ولا يتحقق من النتائج. |
| tool registry/policy/sandbox | **REUSE** | أساس آمن لتوليد artifacts وتشغيل local harness. |
| shell/file tools ضد أنظمة العميل | **DO NOT EXTEND BLINDLY** | تحتاج connectors scoped لا shell حر. |
| output firewall/sanitizers | **REUSE FOR DISPLAY** | ليست verdict gate. |
| HCE domain validators | **KEEP AS PLUGINS/REFERENCE** | مفيدة لاحقًا، ليست قلب OAE. |
| broad offer catalog as public product menu | **DELETE FROM GTM** | يشتت المشتري؛ احتفظ به كأرشيف فرضيات. |
| commercial readiness states | **REUSE** | ممتازة لضبط ادعاء الإيراد. |
| Engagement/Outcome/Scenario/Evidence/Verdict models | **BUILD** | غير موجودة. |
| n8n/webhook connector + downstream verifier | **BUILD** | الفجوة التقنية الرئيسية. |
| evidence packet generator | **BUILD** | المخرج المدفوع. |
| economic event ledger | **BUILD MINIMAL** | إثبات أول معاملة دون billing platform. |

---

# 14. أقل تغيير + أكبر قيمة

درجات 1–5 أدناه **تقييم تحليلي** وليست أرقام سوق.

| المرشح | إعادة استخدام الأصول | قدرة جديدة مطلوبة (5=قليل) | تعقيد الدمج (5=سهل) | دليل الإنفاق | حاجز الثقة (5=منخفض) | المحصلة |
|---|---:|---:|---:|---:|---:|---|
| اشتراك تعليم عالمي | 5 | 2 | 2 | 2 | 3 | لا: market/content/localization heavy |
| تنظيف فواتير أوروبي | 2 | 4 | 4 | 4 | 2 | قابل، لكنه يهمل intelligence core ويتأثر بالقواعد |
| AI red team مؤسسي | 4 | 2 | 2 | 5 | 1 | مال أعلى، credibility/liability أعلى |
| **Workflow Outcome Assurance** | **4** | **3** | **3** | **3** | **3** | **أفضل توازن لأول اختبار** |
| observability SaaS | 3 | 2 | 2 | 4 | 2 | مرفوض: سوق أدوات مزدحم |

سبب اختيار Outcome Assurance ليس أنه الأكبر سوقًا، بل أنه:

1. يستعمل الحوار والتشخيص والحالة والتنفيذ والتحقق معًا.
2. يُسلّم رقميًا بالكامل.
3. يمكن اختباره على workflow واحد دون منصة.
4. يملك trigger قريبًا من المال: handoff.
5. لا يحتاج ادعاء شهادة قانونية أو أمنية.

---

# 15. First Real Economic Workflow

## السيناريو الأول

**Lead intake → AI qualification → CRM → owner assignment → notification/calendar** في n8n.

## السلسلة

```text
MARKET PAIN
workflow يظهر success لكن قد يكرر lead، يخطئ التصنيف، أو يفشل downstream بصمت
↓
PAYING CUSTOMER
مالك/مدير تسليم وكالة أتمتة قبل handoff
↓
DESIRED OUTCOME
إثبات مستقل أن النتيجة التجارية صحيحة تحت happy/failure paths
↓
REQUIRED CAPABILITY
contract extraction + scenarios + execution + downstream verification + evidence
↓
EXISTING CAPABILITY?
conversation/context/planning/tools/review/artifacts = جزئيًا نعم
↓
CODE LOCATION
chat WS, orchestrator graph, agent_tools, generative UI, persistence
↓
MISSING CAPABILITY
n8n/webhook adapter, business assertions, evidence ledger, verdict
↓
NEW COMPONENT
OAE vertical slice
↓
DELIVERABLE
Acceptance Packet + regression scenarios + one retest
↓
ECONOMIC VALUE
تسليم أوضح، كشف partial failures، تقليل rework/nزاع — يُقاس في pilot
↓
HARD-CURRENCY PAYMENT
فاتورة خدمة محدودة من مشترٍ أجنبي وتسوية موثقة
```

## السيناريوهات الأولى

1. valid qualified lead.
2. valid unqualified lead.
3. malformed payload.
4. duplicate event/retry.
5. CRM timeout/5xx.
6. expired credential.
7. LLM uncertain/invalid structured output.
8. forbidden sensitive field.
9. notification failure after CRM success (partial success).
10. repeated run verifies idempotency.

## assertions

- exactly-one CRM record.
- correct fields and owner.
- no forbidden data copied.
- notification status matches policy.
- timeout triggers bounded retry, not duplicate.
- uncertain classification routes to human review.
- observed downstream IDs exist.
- evidence contains versions and timestamps.

---

# 16. First Foreign-Currency Transaction

## صيغة الصفقة المقترحة — كلها فرضية تسعير

**العميل:** وكالة أتمتة فرنسية/بريطانية صغيرة لديها workflow قريب من التسليم.  
**النطاق:** workflow واحد، 8 سيناريوهات، staging فقط، packet، retest واحد.  
**السعر الاختباري:** `€350` **PRICING HYPOTHESIS**؛ ليس سعر سوق مثبتًا.  
**الدفع المقترح:** 50% عند kickoff و50% عند تسليم packet، `Net-7`، بعد تحقق محاسب/بنك من الكيان والفاتورة ومسار القبض.  
**معيار القبول:** تسليم الأدلة المتفق عليها، لا وعد أن verdict سيكون `ACCEPT`. اكتشاف `HOLD` تسليم صحيح.  
**العملة الصعبة الأولى:** لا تُسجّل عند الاتفاق أو الفاتورة؛ تُسجّل عند تسوية الدفعة في القناة المهنية وإرفاق دليلها في سجل تجاري خاص غير عام.

## لماذا €350؟

ليس لأنه «القيمة الحقيقية»، بل لأنه اختبار بين عرض مستقل منشور بـ$149 وسياق مشاريع أتمتة بآلاف الدولارات. المطلوب من التجربة معرفة:

- هل يشتري العميل أصلًا؟
- هل السعر منخفض لدرجة يضر الثقة أم مناسب لأول proof؟
- كم ساعة تسليم حقيقية؟
- هل يدفع العميل أكثر للـdownstream verification أو أقل للاختبار النصي؟

## شرط قتل الصفقة

لا تبدأ إن لم تتأكد قبلها من:

- كيان مخول للفوترة.
- حساب/قناة مهنية قابلة للتوثيق.
- شروط بيانات وNDA/DPA عند الحاجة.
- staging authorization مكتوبة.
- عدم وجود production mutation.

---

# 17. MVP

## ما يُبنى

1. route/feature منفصل باسم assurance؛ لا تغيير المنتج التعليمي العام.
2. خمسة نماذج بيانات: Engagement, OutcomeContract, Scenario, RunEvidence, Verdict.
3. أربع بطاقات UI: contract، scenario plan، run progress، verdict.
4. graph متسلسل: intake → compile → approve → run → verify → review → packet.
5. connector واحد: generic authenticated webhook/n8n test endpoint.
6. verifier أولي: JSON schema، exact/set/count، timing، idempotency، downstream HTTP GET/read-only.
7. artifact: `packet.json` + `packet.md` + checksums.
8. manual commercial ledger: quote/deposit/delivery/settlement status.

## ما لا يُبنى

- billing service.
- multi-tenant SaaS.
- PDF designer.
- 20 connectors.
- continuous monitoring.
- compliance mapping.
- autonomous production remediation.
- custom model training.

## تقدير التغيير النسبي

- **إعادة استخدام مباشرة:** transport، auth، persistence patterns، event protocol، UI shell، tool policy، telemetry.
- **إعادة تصميم:** state، probes، reviewer، artifact registry.
- **بناء جديد مركز:** connector + verifier + evidence schema + verdict.
- **تعقيد غير ضروري متجنب:** خدمة جديدة، DB جديدة، agent society جديدة.

---

# 18. Validation Plan

## المرحلة 0 — 3 أيام: برهان التسليم لا السوق

- ابن workflow synthetic معروف الأخطاء.
- أنتج packet كاملًا يدويًا بمساعدة الكود الحالي.
- تحقق أن شخصًا خارجيًا يستطيع إعادة سيناريو فاشل من packet وحده.
- **فشل المرحلة:** packet لا يتيح reproduction أو verdict لا يرتبط بأدلة.

## المرحلة 1 — 7 أيام: مقابلات المشكلة

- 10 مقابلات مع owners/delivery leads لوكالات n8n/Make/AI صغيرة.
- لا تعرض المنتج أول 15 دقيقة.
- اسأل عن آخر handoff، آخر partial failure، من كتب UAT، كيف أُغلقت الدفعة النهائية، وما الذي لا تثبته logs.
- سجل ألفاظهم وحوادثهم، لا آرائهم العامة عن AI.

**إشارة استمرار:** ثلاث وقائع حديثة على الأقل فيها إعادة عمل/تأخر قبول/فشل downstream، واثنان يشاركان artifact حقيقيًا بعد إخفاء البيانات.  
**إشارة قتل/تحوير:** الجميع يملك QA مستقلًا وacceptance packet كافيًا، أو لا توجد دفعة/مخاطرة مرتبطة بالhandoff.

## المرحلة 2 — 7 أيام: اختبار عرض مدفوع قبل البرمجة

قدّم عرضًا ثابتًا لثلاثة نطاقات فقط:

- 5 scenarios / text+logs only.
- 8 scenarios / downstream read-only verification.
- 8 scenarios + retest.

اطلب deposit حقيقيًا، لا «هل ستدفع؟».

**بوابة:** عرض مدفوع واحد من 30 حسابًا مؤهلًا كحد اختبار مسبق. إن لم يحدث:

- لا تبن المنصة.
- افصل channel failure عن offer failure عبر أسباب الرفض.
- إن كان الألم معترفًا لكن لا ميزانية مستقلة، بع العرض white-label داخل سعر مشروع الوكالة.

## المرحلة 3 — 14 يومًا: paid pilot يدوي-أولًا

قِس:

- ساعات scope/contract.
- ساعات scenario authoring.
- نسبة assertions الحتمية مقابل البشرية.
- عدد failures القابلة لإعادة الإنتاج.
- زمن retest.
- هل استخدم العميل packet في handoff؟
- هل أدت النتيجة إلى دفع نهائي/خفض rework؟ لا تنسب سببية بلا تصريح ودليل.

**بوابة الاقتصاد:** إذا تجاوز التسليم 12 ساعة لسعر €350، فإما رفع السعر، تضييق النطاق، أو قتل النموذج. الرقم حد تشغيلي اختباري، لا benchmark سوق.

## المرحلة 4 — بعد 3 pilots مدفوعة متشابهة فقط

ابن automation للخطوة الأكثر تكرارًا. لا تحول الخدمة إلى SaaS قبل:

- نفس ICP.
- نفس نوع workflow.
- نفس evidence schema.
- نفس verifier class.
- طلب retest/renewal مثبت.

## لوحة الحقيقة

| Claim | Evidence needed | Current state |
|---|---|---|
| الوكالات تعاني من acceptance gap | مقابلات + artifacts | `UNVALIDATED` |
| ستدفع لطرف مستقل | deposit | `UNVALIDATED` |
| الكود يقلل وقت التسليم | manual baseline vs MVP | `UNVALIDATED` |
| packet يساعد handoff | customer use/confirmation | `UNVALIDATED` |
| retest يخلق revenue متكرر | second paid order | `UNVALIDATED` |
| مسار EUR قانوني وعملي | bank/accountant + settled transfer | `UNVALIDATED` |

---

# 19. المخاطر وشروط القتل

| الخطر | لماذا حقيقي | التخفيف | شرط القتل |
|---|---|---|---|
| buyer لا يفصل QA عن build | agency margin pressure | white-label/bundle | 10 اعترافات ألم بلا أي قبول سعر |
| الثقة في طرف جديد منخفضة | الوصول للأنظمة حساس | synthetic/staging/read-only | لا أحد يمنح staging بعد 5 opportunities |
| الأدوات العامة تكفي | LangSmith/Braintrust/open-source | outcome contract + downstream verdict | العميل يحقق نفس packet آليًا بلا عمل إضافي |
| scope explosion | workflow boundaries واسعة | one outcome/one workflow | median delivery لا يمكن ضبطه بعد 3 pilots |
| LLM judge غير موثوق | سوق eval نفسه يقر بذلك | deterministic first + human | معظم assertions تظل subjective |
| مسؤولية أمنية/قانونية | agent workflows قد تكون حساسة | acceptance لا certification | buyer يشترط ضمانًا لا يمكن تأمينه |
| تحصيل الجزائر | موثق داخليًا كفجوة | gate قبل العقد | لا قناة قانونية عملية بتكلفة مقبولة |
| domain leakage | كود التعليم hard-coded | bounded context جديد | يتطلب التغيير كسر المنتج التعليمي بدل عزله |

---

# 20. الخلاصة التنفيذية والقرار

## ما المشروع الذي كان مختبئًا؟

ليس «التعليم + عملة صعبة». التعليم كان مختبرًا بنى ثلاثة أصول نادرة نسبيًا عند اجتماعها:

1. **حوار تشخيصي لا يكتفي بطلب المستخدم الأول.**
2. **حالة وأدلة تتراكم عبر الزمن بدل إجابة منعزلة.**
3. **ثقافة هندسية تفرق بين ادعاء وشيء يمكن إعادة تشغيله.**

وثائق العملة الصعبة أضافت حقيقة اقتصادية مكملة:

> العميل المؤسسي الخارجي لا يدفع للذكاء المجرد؛ يدفع لمخرج محدود، مقبول، قابل للتدقيق، يخفف تكلفة أو مخاطرة داخل workflow قائم.

والبحث الخارجي أضاف القطعة الثالثة:

> سوق AI workflows ينفق على البناء، لكنه يعاني من reliability/observability/eval منفصلة عن سياق التنفيذ والنتيجة؛ وفي الوقت نفسه أصبحت أدوات traces/evals العامة رخيصة ومزدحمة.

إذن التركيب الجديد هو:

```text
Pedagogical diagnosis
+ stateful agent execution
+ evidence-first commercial doctrine
+ workflow reliability gap
=
Outcome Assurance Engine
```

## القرار الواحد

**لا تُحسّن المنتج التعليمي لأجل العملة الصعبة. لا تبن منصة امتثال. لا تبن observability SaaS.**  
اختبر خلال 30 يومًا خدمة واحدة:

> **قبول مستقل قائم على الدليل لعملية AI automation واحدة قبل handoff، يُباع لوكالة تنفيذ أجنبية.**

إذا لم يدفع أحد، تُقتل الأطروحة أو تتغير دون المساس بقيمة التعليم. وإذا دفع عميل واحد ثم كرر ثلاثة عملاء نفس العملية، عندها فقط يصبح من المنطقي تحويل الـvertical slice إلى منتج.

---

# 21. سجل المصادر الخارجية المختصر

## مصادر أولية/رسمية

- النص الموحد لـEU AI Act بعد تعديل 2026: [1](https://eur-lex.europa.eu/eli/reg/2024/1689/2026-07-27/eng).
- Regulation (EU) 2026/1744: [3](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ%3AL_202601744).
- صفحة المفوضية للمواعيد الحالية: [2](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai).
- NIST Generative AI Profile: [1](https://airc.nist.gov/docs/NIST.AI.600-1.GenAI-Profile.ipd.pdf).

## أدلة ألم/تشغيل

- Inngest, 130 engineers, AI in Production 2026: [8](https://www.inngest.com/blog/ai-in-production-report-2026).
- Cleanlab, production AI leaders: [4](https://cleanlab.ai/ai-agents-in-production-2025/).
- KPMG Q4 AI Pulse: [2](https://kpmg.com/us/en/media/news/q4-ai-pulse.html).
- Okta enterprise buyer survey: [4](https://www.okta.com/newsroom/articles/enterprise-buyer-survey-ai-agent-security/).

## بدائل وأسعار منشورة — تُقرأ كسند مورد لا حجم سوق

- LangSmith/Braintrust comparison and pricing: [3](https://www.langchain.com/resources/llm-observability-tools).
- n8n agency pricing example: [1](https://buldrr.com/n8n-automation-agency-pricing/).
- n8n production testing checklist: [4](https://hatchworks.com/blog/ai-agents/n8n-best-practices/).
- Independent acceptance offer: [3](https://community.n8n.io/t/for-hire-independent-acceptance-test-for-one-critical-n8n-workflow-5-scenarios-149-fixed/311749).

> **قاعدة المصدر:** صفحات الموردين ممتازة لإثبات «هذا العرض/السعر منشور»، وضعيفة لإثبات حجم السوق أو متوسط السعر أو النتيجة. الاستبيانات تثبت اتجاهًا داخل عينتها، لا طلبًا منا. والدفع وحده ينقل الأطروحة تجاريًا.
