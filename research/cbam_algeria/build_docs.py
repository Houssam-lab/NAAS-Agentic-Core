from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x55, 0x55, 0x55)

def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def base(doc, rtl=False):
    st = doc.styles['Normal']
    st.font.name = 'Calibri'; st.font.size = Pt(10.5)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)

def h(doc, text, lvl=1, rtl=False):
    p = doc.add_heading(text, lvl)
    for r in p.runs: r.font.color.rgb = NAVY
    if rtl: p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.right_to_left = True
    return p

def para(doc, text, bold=False, italic=False, size=None, color=None, rtl=False, align=None):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    if rtl:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pPr = p._p.get_or_add_pPr(); bidi = OxmlElement('w:bidi'); pPr.append(bidi)
    if align: p.alignment = align
    return p

def bullet(doc, text, rtl=False, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
    p.add_run(text)
    if rtl:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        pPr = p._p.get_or_add_pPr(); pPr.append(OxmlElement('w:bidi'))
    return p

def table(doc, headers, rows, widths=None, rtl=False):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, hd in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ''
        r = c.paragraphs[0].add_run(hd); r.bold = True; r.font.color.rgb = RGBColor(255,255,255); r.font.size = Pt(9.5)
        shade(c, '1F3A5F')
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(9.5)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    if rtl:
        tblPr = t._tbl.tblPr; b = OxmlElement('w:bidiVisual'); tblPr.append(b)
    doc.add_paragraph()
    return t

# =====================================================================
# DOCUMENT 1 — English partner briefing (to share with Green and Fair)
# =====================================================================
d = Document(); base(d)

p = para(d, 'CBAM VERIFICATION IN ALGERIA', bold=True, size=20, color=NAVY, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, 'Market Map & Local Partnership Proposal', size=13, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, 'Prepared for: Green and Fair JSC (Sofia, Bulgaria) — BAS Verification Body No. 12 ОВ', size=10, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, 'Prepared by: Houssam Benmerah — University of El Tarf, Algeria  |  September 2026', size=10, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, 'Confidential — for discussion purposes only. Figures are from public sources and to be validated with installation operators.', italic=True, size=8.5, color=GREY, align=WD_ALIGN_PARAGRAPH.CENTER)

h(d, '1. Executive summary')
para(d, 'Algeria is one of the most CBAM-exposed economies in the Mediterranean and one of the least served by verification capacity. '
        'Three sectors — nitrogen fertilizers, iron & steel, and cement/clinker — account for essentially all of Algeria\'s CBAM-covered exports to the EU, '
        'and they are concentrated in fewer than 15 industrial sites along the coast (Arzew/Oran, Annaba, Jijel, Chlef, Skikda). '
        'This concentration makes Algeria an efficient market: a small number of large installations, each facing a verified-vs-default-value cost gap that can reach tens of millions of euros per year.')
para(d, 'Key facts:', bold=True)
bullet(d, 'The EU is Algeria\'s largest trading partner (49.6% of Algeria\'s international trade in 2025); EU goods imports from Algeria reached €26.5 bn in 2025.')
bullet(d, 'Algeria is one of the top-three suppliers of EU-27 fertilizer imports (with Egypt and the USA) and a key origin for both ammonia and urea.')
bullet(d, 'Algeria became a net steel exporter in 2025 (~1 Mt net). Its EAF/DRI-based steel is marketed to European buyers explicitly on its low carbon footprint — meaning producers have a direct financial incentive to replace default values with verified actual emissions.')
bullet(d, 'A single GICA plant (Chlef/ECDE) exported ~2 Mt of clinker to Europe in 2025 alone.')
bullet(d, 'Indicative CBAM cost for Algerian goods under default values has been estimated at ~€148/tonne — this gap is the commercial argument for verification.')
bullet(d, 'No CBAM verifier is yet accredited anywhere in the EU (as of Aug 2026). The first verification window (Jan–Sep 2027) requires mandatory physical site visits. A locally-based auditor removes travel cost and scheduling risk for the verification body.')

h(d, '2. Target installations — Algeria CBAM market map')
para(d, 'Priority is ranked by (a) volume exported to the EU, (b) CN-code coverage under Annex I of Regulation (EU) 2023/956, and (c) ownership structure (JV partners with European or Gulf shareholders tend to move fastest on compliance).', size=10)

h(d, '2.1 Fertilizers (CN 2814 ammonia, 3102 urea/nitrogen fertilizers, 3105 NPK)', 2)
table(d, ['Installation', 'Location', 'Ownership', 'Capacity / output', 'EU relevance', 'Priority'], [
    ['Sorfert Algérie', 'Arzew (Oran)', 'Fertiglobe/OCI 51% – Sonatrach 49%', '~0.8–1.0 Mt/yr merchant ammonia; 1.3–1.4 Mt/yr granular urea', 'Export-oriented; direct ammonia pipeline to port; Fertiglobe already reports CBAM data to EU customers', 'A'],
    ['AOA (Algerian Omani Fertilizer Co.)', 'Arzew (Oran)', 'Sonatrach/Asmidal – Suhail Bahwan (Oman)', '2024: >2.4 Mt urea, 1.35 Mt ammonia; ~90% of urea exported; 3rd train (+50%) agreed Aug 2026', 'Largest single urea exporter in Algeria', 'A'],
    ['Fertial – Arzew', 'Arzew (Oran)', 'Asmidal/Sonatrach – Grupo Villar Mir (Spain)', 'Ammonia (part of 0.85–1.1 Mt/yr group capacity)', 'Spanish shareholder = EU pull-through', 'A'],
    ['Fertial – Annaba', 'Annaba', 'idem', 'Ammonia + NPK (~200–250 kt/yr NPK lines)', 'Close to Annaba port; EU-facing', 'A'],
    ['Asmidal / other Sonatrach fertilizer units', 'Annaba, Arzew', 'Sonatrach group', 'Nitric acid, ammonium nitrate, UAN (in scope)', 'Secondary', 'B'],
], widths=[3.2, 2.2, 3.4, 3.8, 3.4, 1.2])

h(d, '2.2 Iron & steel (CN 72 & 73 — rebar, wire rod, billets, HRC, plate, DRI, pellets)', 2)
table(d, ['Installation', 'Location', 'Ownership', 'Capacity / output', 'EU relevance', 'Priority'], [
    ['Tosyalı Algérie', 'Bethioua (Oran)', 'Tosyalı Holding (Türkiye)', '~6.2 Mt/yr crude steel (EAF), 5 Mt/yr DRI, ~5.9 Mt/yr rolled; HRC since 2025', 'Targets US$1 bn exports in 2025, mainly to EU (Italy, Spain); shipped 30 kt plate to Italy Mar-2025; US market now closed → EU pivot', 'A+'],
    ['AQS – Algerian Qatari Steel', 'Bellara (Jijel)', 'Qatar Steel Int\'l 49% – SIDER 46% – FNI 5%', '~2.2 Mt/yr steel (EAF), 2 Mt/yr rolled (rebar, wire rod, billets)', 'Exports billets to Europe; Posco export agreement', 'A'],
    ['ALSOLB (ex-Sider El Hadjar)', 'El Hadjar (Annaba)', 'State (SIDER group)', 'BF-BOF; nominal 2 Mt/yr, actual 1–1.5 Mt/yr', 'Coils exported to Italy; higher-carbon route = biggest CBAM cost exposure', 'B'],
    ['Ozmert Algeria & other private re-rollers', 'Various', 'Private (Turkish)', 'Rolling only (precursor emissions from purchased billets)', 'Complex-goods precursor chain', 'C'],
], widths=[3.2, 2.2, 3.4, 3.8, 3.4, 1.2])

h(d, '2.3 Cement & clinker (CN 2523 — clinker, Portland cement, aluminous cement)', 2)
table(d, ['Installation', 'Location', 'Ownership', 'Capacity / output', 'EU relevance', 'Priority'], [
    ['ECDE – Chlef cement plant (GICA)', 'Oued Sly (Chlef)', 'GICA (state)', '3 lines, 4.2 Mt/yr; ~2 Mt clinker exported to Europe in 2025', 'Largest clinker exporter to EU; ships from Ténès & Oran', 'A+'],
    ['Cilas (Biskra)', 'Biskra', 'Souakri 51% – LafargeHolcim Algérie 49%', '2.7 Mt/yr; exports clinker to France via Skikda', 'Holcim group = CBAM-savvy shareholder', 'A'],
    ['LafargeHolcim Algérie (M\'sila, Oggaz)', 'M\'sila, Oran', 'Holcim group', 'Multi-Mt/yr; export programme via Oran/Djendjen', 'Group already manages CBAM in other geographies', 'A'],
    ['Other GICA plants (SCAEK Aïn El Kebira, SCIBS Béni Saf, SCIZ Zahana, Aïn Touta)', 'East & West', 'GICA (state)', 'Combined >10 Mt/yr; several with EU CE conformity', 'Export capacity growing as domestic market is saturated', 'B'],
    ['Biskria Ciment', 'Biskra', 'Private', '~2.7 Mt/yr+', 'Exports to Africa/Europe', 'B'],
], widths=[3.2, 2.2, 3.4, 3.8, 3.4, 1.2])

h(d, '2.4 Other in-scope sectors', 2)
bullet(d, 'Aluminium (CN 76): no primary smelter in Algeria; only downstream extruders/re-melters (e.g. ALGAL+, private profile makers). Low priority.', bold_prefix='')
bullet(d, 'Electricity (CN 2716): no commercial export interconnection to the EU today; the Algeria–Italy subsea link project is at study stage. Not relevant for 2026–2027.')
bullet(d, 'Hydrogen: outside your requested scope; noted only for completeness (SoutH2 corridor project, long-term).')

h(d, '3. Why the verified-vs-default gap matters commercially')
para(d, 'Algerian operators have a structural advantage: gas-fed ammonia, EAF/DRI steel and modern dry-process cement kilns all have direct emission intensities well below EU default values that are set at the level of the worst-performing EU installations (with mark-ups). '
        'For an exporter shipping 1 Mt/yr of urea, a difference of even 0.5 tCO2/t between default and verified actual emissions represents ~500 kt CO2 × EU ETS price (~€70–90) ≈ €35–45 million per year in CBAM certificates borne by their EU customers — and therefore in price competitiveness. '
        'This is the sales pitch: verification is not a compliance cost, it is a margin-protection tool.')

h(d, '4. Proposed cooperation model')
para(d, 'Consistent with your standard approach (local commercial partner + local auditor under your accreditation), I propose a two-layer arrangement:')
table(d, ['Layer', 'Role', 'Scope', 'What Green and Fair keeps'], [
    ['1. Referral / business development', 'Local commercial partner (Algerian legal entity)', 'Identify and qualify installations; first contact; explain CBAM methodology to operators (FR/AR/EN); coordinate pre-verification readiness; logistics for site visits', 'All contracting with clients; pricing; verification opinion'],
    ['2. Auditor agreement', 'Houssam Benmerah as local auditor within Green and Fair\'s verification team', 'Document review, data checks, site visits, sampling, working papers — under supervision of a G&F lead verifier; competence path per ISO 14065 / 14066 and IR (EU) 2025/2546', 'Technical review, independent review, issuance of verification report, accreditation responsibility'],
], widths=[3.5, 3.8, 6.2, 3.7])
para(d, 'Impartiality safeguard: where I originate a client, a different G&F auditor performs the engagement, or my role is limited to non-decision tasks, per your impartiality procedures. This keeps the model clean under BAS oversight.', italic=True, size=10)

h(d, '5. What I bring')
bullet(d, 'Academic affiliation (University of El Tarf) — perceived neutrality and credibility with state-owned groups (Sonatrach/Asmidal, GICA, SIDER), which dominate the target list.')
bullet(d, 'Trilingual (Arabic / French / English) — all Algerian technical documentation and site communication is in French/Arabic.')
bullet(d, 'Geographic position: El Tarf–Annaba is within 1 hour of Fertial Annaba, ALSOLB El Hadjar and Annaba port; Jijel (AQS) and Skikda are 2–3 hours away. Western cluster (Arzew, Oran, Chlef) reachable by domestic flight.')
bullet(d, 'Ability to remove the single biggest bottleneck for the 2027 verification window: mandatory physical site visits without EU-based staff travel.')
bullet(d, 'Research and data discipline — structured evidence gathering and documentation, which is what audit working papers require.')

h(d, '6. Proposed next steps')
table(d, ['#', 'Step', 'Owner', 'Timing'], [
    ['1', 'Call to align on model, competence path and commercial terms', 'Both', 'Wed 23 Sep 2026, 15:30 Algiers'],
    ['2', 'NDA + draft auditor agreement + referral term sheet', 'G&F', 'Week of 28 Sep'],
    ['3', 'Confirm status of CBAM scope extension application at BAS (DR 2025/2551) and expected date', 'G&F', 'At call'],
    ['4', 'Auditor onboarding: training (ISO 14064-3, IR 2025/2546, IR 2025/2547 methodology), shadowing plan', 'G&F / HB', 'Oct–Nov 2026'],
    ['5', 'Set up Algerian contracting entity for referral layer', 'HB', 'Oct 2026'],
    ['6', 'First outreach wave: 5 priority-A installations (readiness assessment offer)', 'HB with G&F materials', 'Nov–Dec 2026'],
    ['7', 'First verification engagements', 'G&F team + HB', 'Q1–Q2 2027'],
], widths=[0.8, 9, 3, 4.2])

h(d, '7. Points to agree at the call')
bullet(d, 'Auditor daily rate (EUR), expenses policy, and payment channel to Algeria.')
bullet(d, 'Referral fee: % of first-year contract value vs. recurring; payable on client payment.')
bullet(d, 'Exclusivity for Algeria (mutual) and its duration/performance conditions.')
bullet(d, 'Who bears training/qualification cost; timeline to "approved auditor" status under your management system.')
bullet(d, 'Handling of Algerian foreign-exchange rules for service payments in EUR.')

para(d, ' ')
para(d, 'Sources (public): European Commission DG TRADE – EU–Algeria trade picture 2025; BAS register (nab-bas.bg) – Green and Fair JSC No. 12 ОВ; Fertiglobe corporate site; Oman Observer (AOA expansion, Aug 2026); APS (Tosyalı exports 2025; Chlef clinker exports 2025); GMK Center (Algerian steel industry, 2026); TSA / CemNet (Cilas, ECDE); cbamguide.com accreditation tracker (Aug 2026); carboneer.earth CBAM verification guidance (2026); Carra Globe CBAM 2026 default-value cost estimate; co2-iq.com (EU CBAM import volumes 2024).', size=8, color=GREY)

d.save('/home/user/cbam_algeria/CBAM_Algeria_Market_Map_and_Partnership_Proposal.docx')

# =====================================================================
# DOCUMENT 2 — Arabic private call playbook (for Houssam only)
# =====================================================================
a = Document(); base(a)
para(a, 'دليل المكالمة الخاص — Green and Fair (الأربعاء 23 سبتمبر 2026 – 15:30)', bold=True, size=16, color=NAVY, rtl=True)
para(a, 'وثيقة داخلية لك فقط — لا تُرسل', italic=True, color=GREY, rtl=True)

h(a, '1. الهدف من المكالمة', rtl=True)
bullet(a, 'الخروج بـ: (أ) موافقة مبدئية على دورك كمدقق محلي، (ب) موافقة مبدئية على نموذج إحالة، (ج) وعد بإرسال مسودة العقدين + NDA.', rtl=True)
bullet(a, 'ليس الهدف الاتفاق على كل الأرقام، بل الحصول على نطاقات (ranges) واضحة.', rtl=True)

h(a, '2. السيناريو (20–30 دقيقة)', rtl=True)
table(a, ['الوقت', 'المرحلة', 'ما تقوله'], [
    ['0–2 د', 'افتتاح', 'شكر + "أرسلت لك قبل المكالمة خريطة السوق الجزائري، أقترح أن نمر عليها سريعاً ثم نناقش نموذج التعاون".'],
    ['2–8 د', 'عرض القيمة', 'الجزائر = 3 قطاعات مركزة في أقل من 15 موقعاً. اذكر الأسماء بثقة: Sorfert، AOA، Fertial، Tosyalı، AQS، ECDE Chlef، Cilas. "هذه ليست سوقاً منتشرة؛ إنها 10 عقود كبيرة".'],
    ['8–12 د', 'جواب سؤال "freelancer or company?"', '"حالياً بصفة مستقلة مع انتماء جامعي. للإحالة سأتعاقد عبر كيان جزائري (قيد الإنشاء أو شريك). للتدقيق، اتفاق فردي معي مباشرة كما هو نموذجكم". لا تقل "freelancer" وحدها.'],
    ['12–20 د', 'أسئلتك', 'انظر القسم 3.'],
    ['20–25 د', 'الشروط', 'اطلب نطاقات: أجر يومي، نسبة إحالة، حصرية. إن قال "سنرسلها كتابياً" فاقبل واطلب موعداً.'],
    ['25–30 د', 'إغلاق', 'لخّص الخطوات التالية بصوت عالٍ + "سأرسل ملخصاً بالبريد اليوم".'],
], widths=[1.6, 3.4, 12], rtl=True)

h(a, '3. أسئلة يجب أن تطرحها (بالترتيب)', rtl=True)
bullet(a, 'ما وضع طلب توسيع نطاق الاعتماد لـ CBAM لدى BAS؟ هل قُدّم، وما التاريخ المتوقع؟ (تسجيلكم الحالي رقم 12 ОВ يغطي EU ETS — وهذا ما رأيته في سجل BAS).', rtl=True, bold_prefix='الاعتماد: ')
bullet(a, 'ما مسار التأهيل: تدريب ISO 14064-3 / 14065 / 14066 + منهجية CBAM (IR 2025/2547)؟ كم مهمة مرافقة (shadowing) قبل الاستقلالية؟ من يدفع التدريب؟', rtl=True, bold_prefix='التأهيل: ')
bullet(a, 'الأجر اليومي بالأورو؟ أيام التحضير والتقرير محسوبة أم الزيارة الميدانية فقط؟ المصاريف (سفر داخلي، إقامة)؟', rtl=True, bold_prefix='التدقيق: ')
bullet(a, 'نسبة من قيمة العقد؟ سنة أولى فقط أم متكررة؟ تُدفع عند تحصيلكم من العميل؟', rtl=True, bold_prefix='الإحالة: ')
bullet(a, 'هل تطلبون حصرية للجزائر؟ إن نعم: متبادلة + مشروطة بأداء + مدة سنتين قابلة للتجديد.', rtl=True, bold_prefix='الحصرية: ')
bullet(a, 'كيف تفصلون بين من يجلب العميل ومن يدققه؟ (سؤال يرفع مصداقيتك كثيراً).', rtl=True, bold_prefix='الحياد: ')
bullet(a, 'العملة والقناة: تحويل بالأورو إلى حساب جزائري (حساب بالعملة الصعبة) — هل تعاملتم مع بلدان بقيود صرف مماثلة؟', rtl=True, bold_prefix='الدفع: ')

h(a, '4. أرقام مرجعية للتفاوض (للاسترشاد فقط)', rtl=True)
table(a, ['البند', 'نطاق معقول في السوق', 'ملاحظة'], [
    ['أجر مدقق محلي (خارج EU)', '250–450 € / يوم للمبتدئ تحت إشراف؛ 500–800 € بعد الاعتماد الداخلي', 'ابدأ من الأعلى واقبل الوسط'],
    ['رسوم الإحالة', '10–20% من قيمة عقد السنة الأولى', 'اطلب 15% + نسبة أقل (5–10%) على التجديدات'],
    ['قيمة عقد تحقق CBAM لمنشأة كبيرة', 'من 15–20 ألف € إلى 50 ألف €+ حسب التعقيد وعدد المنتجات', 'أي أن إحالة واحدة = 2–7 آلاف €'],
    ['مصاريف', 'تُغطى بالكامل مقابل فواتير', 'لا تقبل أجراً شاملاً للمصاريف'],
], widths=[5, 6.5, 5.5], rtl=True)
para(a, 'هذه تقديرات سوقية عامة وليست عروضاً؛ استخدمها لتعرف إن كان عرضه منطقياً.', italic=True, size=9, color=GREY, rtl=True)

h(a, '5. خطوط حمراء', rtl=True)
bullet(a, 'لا عمل على بيانات عملاء قبل NDA وعقد موقّع (قلتها في رسالتك — التزم بها).', rtl=True)
bullet(a, 'لا تقديم نفسك كـ"محقق معتمد" قبل تأهيلك رسمياً لديهم — هذا خطر قانوني عليك وعليهم.', rtl=True)
bullet(a, 'لا حصرية من طرف واحد بدون التزام أداء متبادل.', rtl=True)
bullet(a, 'لا دفع أي رسوم منك لهم (تدريب مدفوع مسبقاً إلخ). إن طُلب ذلك = علامة إنذار.', rtl=True)

h(a, '6. بعد المكالمة (خلال ساعتين)', rtl=True)
bullet(a, 'إيميل ملخص: ما اتُّفق عليه، ما بقي معلقاً، الخطوة التالية بتاريخ.', rtl=True)
bullet(a, 'ابدأ إجراءات كيان قانوني (auto-entrepreneur / EURL) بنشاط "استشارات وخدمات دعم تقني".', rtl=True)
bullet(a, 'حضّر رسالة تعريف موحدة (FR) للمنشآت ذات الأولوية A — لا تُرسلها قبل موافقة G&F على المحتوى.', rtl=True)

a.save('/home/user/cbam_algeria/دليل_المكالمة_الخاص.docx')
print('done')
