# ATS Behavior and Resume Screening in 2026: Evidence Base

Status: background and historical evidence. This file records what is known, with sources, about how applicant tracking systems (ATS) and human reviewers handle resumes in 2026. Its companion, `resume-fit-guidance.md`, turns this evidence into formatting, content, and application rules, audits the `resume-fit` skill, and lists proposed changes. This file owns all source IDs; the guidance file cites them.

Prepared: 2026-10-03. Revised the same day after a third verification pass, then split from the original combined report (its index is archived at `archive/ats-and-resume-screening-2026.md`). All sources accessed 2026-10-03.

## Scope and method

This document covers how ATS platforms parse, rank, and filter resumes in 2026, how human reviewers read them, what big-tech employers officially say, which popular claims are myths, and the regulatory context. It was produced to ground the `resume-fit` skill in evidence rather than folklore. The project decision not to build a replica ATS stands: employers configure their own filters, vendors keep their algorithms proprietary, and optimizing against an in-house model would overfit to that model.

Evidence was gathered on 2026-10-03 in two passes: an automated multi-source research run, followed by a manual pass that re-opened the most load-bearing vendor documents and added material on how systems score required and preferred qualifications. A third pass reviewed two parallel research reports produced for the same brief (a Gemini Deep Research report and a Gemini Antigravity report, archived as `archive/ats-and-resume-screening-2026-antigravity.md`). Only claims whose underlying sources were opened and confirmed were carried into this document; sources S89 to S98 come from that pass. Sources re-opened and checked in the manual or third pass are marked "re-checked" in the bibliography. The rest are carried from the research run and were not individually re-opened.

Source tiers, as defined in the research brief:

| Tier | Meaning |
|---|---|
| 1 | Vendor documentation or official company career pages |
| 2 | Peer-reviewed or methodologically described studies and audits |
| 3 | Reputable industry research, major press, and professional legal analysis |
| 4 | Recruiter or practitioner blogs and first-hand personal accounts |
| 5 | Marketing content from resume-tool vendors (flagged; never used alone for a claim) |

Confidence levels: **high** means tier-1 or tier-2 sources state the claim directly and nothing credible contradicts it. **Medium** means the claim rests on consistent but weaker sources, or on absence of evidence across the documents reviewed. **Low** means sources are thin, conflicting, or only tier 4 or 5.

Citations use bibliography IDs in square brackets, for example [S1].

Two further ID types appear: [L1] and later L-numbers are local tests run for this project, and [U1] marks an unsourced input reviewed but not relied on. Both are described in "Local tests and unsourced inputs" below.

## Executive summary

1. **Workday dominates large enterprise; Greenhouse, Lever, and Ashby dominate venture-backed tech.** Two independent tier-5 datasets agree directionally: Workday at 39.2% of the Fortune 500 [S45] (a second vendor dataset reports over 40% [S90]), and Greenhouse first among a broad set of tech-leaning employers [S45, S46]. No tier-1 or tier-3 market census was found. Confidence: medium.
2. **A failed parse usually produces a degraded record, not a rejection.** Greenhouse attaches the file and requires manual entry when parsing fails, and partial parses "need to be manually corrected" [S1]. Only its email-intake path fails to create the candidate [S2]. Confidence: high.
3. **The documented parse breakers are structural, not typographic.** Greenhouse lists tables, headers, footers, columns, text boxes, contact details in headers or footers, graphics, image-only files, letter-spaced text, inconsistent section formats, abbreviated job titles, and files over 2.5 MB [S1]. Google caps uploads at 2 MB [S3]. Confidence: high.
4. **No vendor source supports flagging em dashes, en dashes, curly quotes, or ampersands as parse failures.** None of the tier-1 or tier-2 documents reviewed mention them [S1, S3, S4]. Confidence: medium, because this is absence of evidence.
5. **Required and preferred qualifications are scored differently by different systems.** Workday HiredScore (August 2026 logic, opt-in) gates A/B versus C/D grades on meeting every basic qualification and uses preferred qualifications to rank within a band [S29]. Greenhouse uses recruiter-assigned weights with no gate [S13]. Ashby returns a meets / does not meet / undecided verdict per criterion and no total score [S30, S32]. Textkernel turns "must-have" terms into hard filters [S33, S34]. Confidence: high for what each vendor documents.
6. **AI ranking is semantic and criteria-calibrated, and every vendor reviewed calls it assistive.** Greenhouse says Talent Matching does not advance or reject candidates [S14], and multiple resume terms can map to one calibrated skill, so synonym repetition does not raise the score [S12]. Eightfold [S35] and LinkedIn [S36] state that their AI makes no autonomous decisions. Confidence: high for documented design, low for how each employer actually uses the rankings.
7. **Automatic rejection is real, but it comes from recruiter-configured application questions.** Greenhouse Auto-Reject [S15, S16], Lever auto-screening [S21], and Workday disqualification questionnaires [S22, S23] all act on answers to application questions. Prevalence: no reliable source found. Confidence: high on mechanism.
8. **Regulation is pushing toward disclosure and human review, on delayed timelines.** NYC Local Law 144 has been enforced since 2023, but a state audit called enforcement ineffective [S50]. EU AI Act obligations for high-risk hiring systems moved to December 2, 2027 [S52, S53]. Colorado replaced its 2024 act with SB 26-189, effective January 1, 2027 [S54, S55]. Mobley v. Workday is a certified collective action with no ruling on the merits yet [S61, S62]. Federally, the EEOC withdrew its AI guidance in early 2025, but Title VII disparate-impact claims remain available through private suits [S91]. Confidence: high.
9. **"75% of resumes are rejected by ATS" has no published method.** The Hidden Workers report, often cited alongside it, measures employer perception: 88% of employers agree qualified high-skill candidates are vetted out for not matching exact criteria. It reports no machine rejection rate [S85]. Confidence: high on what Hidden Workers says, low on the exact origin story of the 75% figure.
10. **No major ATS documents detecting AI-written resume text.** Greenhouse's fraud tooling uses identity and network signals [S18, S19], and peer-reviewed work found seven GPT-text detectors flagged non-native English essays as AI-generated at an average false-positive rate of 61.22% [S65]. Confidence: medium, since Greenhouse was the only ATS checked directly.

## Section A: How ATS platforms work in 2026

### A1. Which platforms dominate tech hiring

| Segment | Dominant platforms | Evidence | Confidence |
|---|---|---|---|
| Fortune 500 and large enterprise | Workday 39.2%, SAP SuccessFactors 13.2% | Jobscan 2025 report, based on a manual review of all 500 career pages [S45] (tier 5) | Medium |
| Broad set of employers that job seekers target | Greenhouse 19.3%, Lever 16.6%, Workday 15.9%, iCIMS 15.3% | Jobscan scan data across 12,820 companies [S45] (tier 5; self-selected sample) | Medium-low |
| Top-rated employers | Greenhouse 49.0%, Workday 21.8%, Lever 8.0% | ResumeGeni crawl of 3,222 employers [S46] (tier 5) | Medium-low |
| AI-native and venture-backed startups | Ashby | 2,700+ customers as of July 2025, per Crunchbase News as relayed by [S48] (tier 4). The research run also reported an Ashby press release (May 7, 2026) claiming use by nearly 70% of the Forbes AI 50; the primary URL could not be retrieved, so treat that figure as unverified | Low-medium |
| Vendor scale | Greenhouse 7,500+ customers [S48]; Workday used by over 11,000 organizations [S64] | Tier 4 relay; tier 3 | Medium |

Market-size estimates disagree sharply. Mordor Intelligence sizes the ATS market at about USD 2.65 billion in 2026 and describes Greenhouse as dominant in technology firms without giving a share figure [S47] (tier 3). Pin's July 2026 report lists analyst estimates ranging from USD 2.5 billion (Apps Run The World, 2024) to USD 17.22 billion (Fortune Business Insights, 2025), a 6.9x spread [S90] (tier 5 relaying tier 3). Any single market-size figure should be treated as low confidence. No tier-3 analyst source (Gartner, SHRM) with vendor share by company size was found.

Two further data points on the enterprise tier. SAP completed its acquisition of SmartRecruiters on September 11, 2025, and is integrating it into the SAP SuccessFactors suite while letting existing customers keep it standalone [S89] (tier 1), so SmartRecruiters now belongs with the enterprise HCM vendors rather than the lightweight tools. In 2019, Workday held 22.6% of the Fortune 500 and Oracle Taleo 22.4%, per Ongig data reported by SHRM [S94] (tier 3, outdated). Read against the 2025 figures [S45, S90], Workday has roughly doubled its Fortune 500 share while Taleo has fallen out of the leading group; the two datasets use different methods, so the trend is directional only.

Practical rule: the apply URL usually names the system (`myworkdayjobs.com`, `boards.greenhouse.io`, `jobs.lever.co`, `jobs.ashbyhq.com`). Some employers run more than one ATS, so check each posting rather than each company.

### A2. Parsing: engines and failure modes

**Parsing engines.** Most ATS vendors do not say which parser they use.

| ATS | Parsing engine | Evidence | Confidence |
|---|---|---|---|
| SAP SuccessFactors | Textkernel | SAP Help Portal [S8] (tier 1) | High |
| Bullhorn | Textkernel (rollout ongoing) | Bullhorn knowledge base [S9]; Bullhorn acquired Textkernel in 2024, and Textkernel had acquired Sovren [S7] (tier 1) | High |
| iCIMS | Secondary sources conflict (Sovren/Textkernel vs. HireAbility) | Tier 4 and 5 only | Low: no reliable source found |
| Greenhouse | Not disclosed. Greenhouse documents 28 parse languages and a 2.5 MB limit but names no vendor | [S1, S11] (tier 1) | No reliable source found |
| Workday, Lever, Ashby, SmartRecruiters, Oracle Taleo | Not disclosed | None found | No reliable source found |

Textkernel's documentation says its parser covers 25 resume languages and 70+ file formats and extracts 50+ fields. It returns an error on scanned images and tells integrators to always send the original file, not a copy-paste, conversion, or scan [S4, S5] (tier 1). Textkernel also offers an LLM-based parser mode [S6] (tier 1; press coverage in [S49]). Daxtra, another commercial parser, says it integrates with Bullhorn, Vincere, JobAdder, and iCIMS [S10] (tier 1, vendor), which does not settle which engine iCIMS uses by default.

**Documented failure modes.** Greenhouse's "Unsuccessful resume parse" article (updated March 2, 2026) is the most specific vendor list found [S1]:

- files over 2.5 MB, often caused by high-resolution images;
- graphics, photos, or word art, and resumes uploaded as images rather than .docx or .pdf;
- complex layouts with tables, headers, and footers;
- name and contact information placed in a header, footer, or text box;
- multi-column layouts;
- missing section structure, or sections formatted inconsistently;
- letter-spaced text;
- company names without identifiers such as Inc., Co., LTD, or LLC;
- abbreviated job titles, such as "Sr. Account Exec" instead of "Senior Account Executive";
- placeholder data such as "Company 1", which is skipped.

Google's own careers portal has a hard 2 MB resume limit, and Google tells candidates its parser may not get complete or accurate data and that they should fill in missed fields by hand [S3] (tier 1).

**Not documented as failure modes.** No tier-1 or tier-2 source was found that lists em dashes, en dashes, curly quotes, ampersands, or particular date formats as parse failures. For unusual fonts, no reliable source was found either; letter-spacing [S1] is the closest documented issue.

**PDF vs .docx.** Greenhouse and Google both accept .pdf and .docx [S1, S3]. Image-only files fail [S1, S4]. One tier-5 source claims Workday prefers DOCX [S87]; tier-1 acceptance of both formats outweighs it. Confidence: medium that a text-based, single-column PDF and a .docx parse comparably.

**Direct test of characters and layout.** The only direct test found is a June 2026 benchmark by ATSVerification, a company that sells resume-scanning tools [S93] (tier 5). It rendered one finance resume in six layouts and ran each through a pdf.js-based text extractor, not a commercial ATS parser. Em dashes and curly quotes did not break extraction. A two-column sidebar layout scrambled reading order, a repeated page header caused the email address to be extracted three times, and creative section headings were flagged as missing standard headings. A single resume on a single open-source extractor is weak evidence, but it points the same way as the vendor documentation: layout breaks extraction, ordinary punctuation does not [S1].

**Local test of a generated resume (L1).** A project test on 2026-10-03 built a .docx with python-docx (the library `render_docx.py` uses), exported it to PDF with LibreOffice, and extracted the text with poppler's `pdftotext` [L1]. Em dashes and curly quotes came through as clean Unicode, and no ligature substitution appeared. The default "List Bullet" glyph extracted as U+F0B7, a private-use character from the Symbol font, which is the kind of corrupt marker resume advice usually attributes to decorative bullets. Header text was extracted rather than dropped. One environment, not a commercial parser; see L1 for limits.

**Effect of a failed parse.** A failed parse attaches the resume and requires manual data entry [S1]. Through Greenhouse Maildrop (email intake), a failed parse means the candidate is not added until someone adds them by hand [S2]. In AI-ranked flows, an unparsed resume is labeled "Needs manual review" rather than scored [S12, S13].

### A3. Ranking and filtering

There are two separate mechanisms, and the skill should not conflate them:

1. **Rule-based filtering** on application answers (knockout questions; see A4). This is deterministic, configured by recruiters, and can reject automatically.
2. **Scoring and ranking** of the parsed resume against job criteria. Every vendor reviewed documents this as decision support. Recruiter keyword search inside the ATS is a third, manual path, and it is where literal terms matter most: a recruiter searching for a specific technology will not find a resume that only implies it. That claim rests on tier-4 and tier-5 descriptions of Greenhouse search; the Greenhouse search documentation itself was not retrieved.

#### A3.1 How systems score hard and soft requirements

The question splits along two axes: required versus preferred qualifications ("requirement level"), and technical versus soft skills ("requirement type").

**Requirement level, by system:**

| System | Required (basic) qualifications | Preferred qualifications | Output | Source |
|---|---|---|---|---|
| Workday HiredScore Spotlight, August 2026 logic | An LLM evaluates "each screenable qualification individually" against the parsed resume. Candidates who meet all basic qualifications receive A or B; the rest receive C or D | Differentiate the grade within a band | A to D grade, plus a met / not met verdict for each qualification, with an explanation and a pointer to the supporting resume section | [S28, S29] (tier 1, re-checked) |
| Greenhouse Talent Matching | No gate. The recruiter weights each criterion, and Greenhouse advises giving "higher weights to non-negotiable requirements" | Lower weights, "to avoid screening out otherwise qualified candidates" | Strong / Good / Partial / Limited / Needs manual review | [S12, S13] (tier 1, re-checked) |
| Ashby AI-assisted review | Not distinguished. Each criterion is a recruiter-written prompt | Not distinguished | Meets / does not meet / undecided for each criterion. No applicant-level score; about 11.4% of evaluations in the audit sample came back uncertain | [S30, S31, S32] (tier 1 and 2, re-checked) |
| Textkernel Search & Match | "Must-have" (and "must-not-have") act as hard filters | "Nice-to-have" and "should-have" carry increasing weight | Score from 0 to 1; each criterion takes a fixed share of the score (job title might be 30%, for example) | [S33, S34] (tier 1, re-checked) |
| Eightfold Matching Model | Not documented | Not documented | Predicted match from 0 to 5 in half-point steps, with skill, work, and title relevance explanations | [S35] (tier 1, re-checked) |
| LinkedIn Hiring Assistant | Recruiter qualifications are turned into search queries | Not distinguished | Ranked list showing which qualifications were found and which are missing | [S36] (tier 1, re-checked) |
| iCIMS | Not documented. The product page says only that it ranks candidates based on skills and experience | Not documented | Not documented | [S37] (tier 1 marketing page, re-checked) |
| Lever | No ranking documentation retrieved | | | No reliable source found |

The structural difference matters more than any keyword count. Under Workday's August 2026 logic, one unmet basic qualification drops a candidate to C or D regardless of other strengths [S29]. Under Greenhouse calibration and Textkernel's should-have tier, strength elsewhere can partly offset a miss [S13, S33]. Ashby produces no ranking score at all [S32]. Two caveats on Workday: the LLM-based Fit & Gap grading is opt-in, rolled out first through a pilot [S29], and the earlier grading logic is not documented [S25, S26, S27]. Whether a given Workday employer gates on basic qualifications depends on its configuration.

**Mechanics that bear on resume text:**

- **Synonym repetition does not stack.** Greenhouse maps related resume terms to one calibrated skill, so "a longer list of matched terms doesn't always mean a higher match score" [S12].
- **Recency and placement count.** Textkernel scores recent job titles higher and weights a skill more when it appears in a recent position [S33]. Weights also shift with context: location drops out for remote jobs, and IT skills count more for IT-domain jobs [S33, S34].
- **Parsers time-stamp skills.** RChilli records which section each skill came from, along with `ExperienceInMonths` and `LastUsed` for each skill [S39]. Inference, not documented: a skill that appears only in a Skills list, outside any dated role, contributes less evidence toward a "years of X" requirement than the same skill inside a dated role.
- **Signals beyond the parsed fields.** Textkernel says semantic signals not visible in the structured parse can affect scores [S34].

**Requirement type (soft skills).** Parsers do extract soft skills as their own type. RChilli has a "Soft Skills" category drawn from summaries and personal statements [S38, S39]. Lightcast, a skills taxonomy that Affinda's parser can map to [S41], classifies communication-type skills as "common skills" found across many occupations [S40]. At the scoring stage, vendors steer employers away from scoring soft skills. Greenhouse's policy guide tells employers to calibrate on "objective, job-related requirements" and to prohibit proxies such as "culture fit" or "personal traits unrelated to job performance" [S13]. Ashby recommends criteria that are "objectively verifiable" and flags criteria that may raise equal-employment concerns [S30]. The exception is LLM-based evaluation: LinkedIn says its AI-assisted search can match unlisted qualifications such as "excellent written and communication skills" [S36], and Workday says Fit & Gap handles non-numeric requirements [S28].

Inference, labeled as such because no vendor publishes a soft-skill weight: a bare list of soft-skill adjectives is a weak signal, since common skills appear on most resumes and do little to separate candidates. Where an LLM evaluator does assess a soft requirement, it most plausibly judges the evidence in the bullets (scope, cross-functional influence, communication outcomes) rather than the word itself.

#### A3.2 Do systems auto-reject?

Rule-based auto-rejection on application answers is documented (A4). AI scoring is documented as assistive [S12, S14, S35, S36]. Inference: in a queue of hundreds of applicants, a low-ranked candidate may never be opened, which works like a rejection without being one. No study quantifying this was found. The only survey-style evidence on configuration is weak: Enhancv, a resume-builder company, interviewed 25 US recruiters in 2025 and reported that 92% do not configure their ATS to auto-reject on resume content, as relayed by a practitioner blog [S97] (tier 4 relaying tier 5; the Enhancv original was not opened). Confidence: medium-low.

#### A3.3 Regulatory context

| Regime | Status as of October 2026 | Relevance | Sources | Confidence |
|---|---|---|---|---|
| NYC Local Law 144 (automated employment decision tools) | Enforced since July 5, 2023: annual independent bias audit, public summary, 10-business-day candidate notice. A New York State Comptroller audit (December 2, 2025) found enforcement ineffective | Employers scoring NYC applicants must disclose. Vendors publish audits, for example [S32, S35] | [S50, S51] | High |
| EU AI Act | Recruitment and candidate filtering are high-risk uses under Annex III. The Digital Omnibus moved those obligations from August 2, 2026 to December 2, 2027; Article 50 transparency duties still applied from August 2, 2026 | Delayed, not repealed | [S52, S53] | High |
| Colorado | SB 24-205 was replaced by SB 26-189, effective January 1, 2027, focused on notice, post-decision disclosure, correction rights, and human review. Most firms report a May 14, 2026 signing date [S54, S55]; one reports May 20 [S56]. May 14 is weighted more because more sources agree. The attorney general is reported not to be enforcing until rulemaking concludes [S57] | Disclosure and review rights from 2027 | [S54, S55, S56, S57, S58, S59] | High on replacement, medium on enforcement timing |
| Illinois | HB 3773 (Public Act 103-0804), effective January 1, 2026, amends the Human Rights Act to cover AI in employment | Anti-discrimination coverage | [S60] | Medium (details not re-verified) |
| California | Civil Rights Council regulations on automated decision systems, effective October 1, 2025 | Anti-discrimination liability | [S60] | Medium |
| US federal (EEOC) | The EEOC withdrew its AI technical guidance or marked it potentially out of date in early 2025, following a presidential executive order on AI. Title VII disparate-impact liability itself is unchanged, and applicants can still sue over discriminatory AI tools | Less federal agency enforcement; private litigation risk remains | [S91] (tier 3) | High on the withdrawal; exact withdrawal date not confirmed |
| Mobley v. Workday, 3:23-cv-00770 (N.D. Cal.) | Preliminary age-discrimination (ADEA) collective certified May 16, 2025; extended in July 2025 to applicants scored with HiredScore features; notice plan approved December 2, 2025. The disparate-impact theory proceeds; no merits ruling yet | Courts may treat AI vendors as agents of employers | [S61, S62, S63, S64] | High |

Interpretation: the legal trend reinforces vendors presenting AI as ranking plus a human decision, and it is adding candidate notices and AI opt-outs. Greenhouse already supports an opt-out that routes the application to manual review [S12, S13].

#### A3.4 Evidence beyond vendor documentation

**One staffing firm's matching pipeline.** A September 2026 preprint by ManpowerGroup Services India and IIT Hyderabad describes a candidate-job matching system for high-volume staffing that combines BM25 keyword scoring with dense embedding retrieval, merged by Reciprocal Rank Fusion inside Azure Cosmos DB, and evaluates it against submission outcomes drawn from ATS records [S92] (tier 2 preprint). It shows that hybrid keyword-plus-embedding matching is in production at a large staffing firm, and that BM25 is kept specifically to preserve exact matching on tokens such as certification codes. It is not evidence of how Workday, Greenhouse, or other ATS vendors rank applicants; none of their documentation describes this architecture.

**Bias in LLM evaluators.** Two 2026 preprints bear on LLM-based screening, including the LLM-run recruiter simulation in this skill. ICE-Guard tested 11 LLMs from 8 families on 3,000 decision scenarios across 10 high-stakes domains and found mean bias rates of 5.8% from authority cues, 5.0% from framing, and 2.2% demographic, with large variation by domain [S95] (tier 2 preprint). The abstract does not confirm that hiring is one of the 10 domains. A separate study of hiring decisions in a Japanese context found a significant pro-female bias across all five models tested, including Claude Sonnet 4.6 and GPT-4o [S96] (tier 2 preprint). Together they indicate that LLM screening verdicts can shift with presentation and identity cues unrelated to qualifications. Confidence: medium, since both are preprints and neither tests a commercial ATS.

### A4. Knockout questions

All documented mechanisms are tier 1:

- **Greenhouse** Auto-Reject rules screen and reject candidates based on custom application questions. When Auto-Advance and Auto-Reject both trigger, Auto-Reject wins. Greenhouse's own example rejects a "No" to a relocation question [S15, S16]. Greenhouse's candidate blog says these rules are set by recruiters, and that more than half of roles send an email on auto-rejection [S17].
- **Lever** auto-screening questions can archive, email, and tag candidates by their answers [S21].
- **Workday** questionnaires can serve as disqualification questions, and its Screen subprocess filters out candidates who miss basic criteria. Answers carry across requisitions that use the same questionnaire [S22, S23, S24].

Prevalence: no reliable source found for the share of tech postings that use knockout questions. Interaction with the resume: the rules evaluate the answers, not the resume text, but reviewers see both, so a mismatch between them (location, relocation, work authorization, years of experience) is a likely source of friction. That last point is inference. Confidence: high on mechanism, low on prevalence.

### A5. AI-generated resume detection

- **ATS vendors.** Greenhouse Fraud Detection uses an IP-reputation service (IPQS) and IP addresses to flag suspicious applications [S18]. Its Real Talent product adds CLEAR identity verification [S19], and its launch announcement targets spam, bots, and fraud patterns [S20]. None of this is a text classifier. The research run reported that Ashby shipped fraudulent-candidate detection in September 2025, but this was not verified against Ashby documentation.
- **Third-party add-ons** claim to flag AI-generated resumes inside Greenhouse but publish no accuracy data [S66, S67] (tier 5).
- **Detector reliability.** Liang et al. (2023) ran seven widely used GPT detectors on 91 TOEFL essays written by non-native English speakers without AI help; the detectors misclassified more than half as AI-generated, at an average false-positive rate of 61.22%, while scoring US eighth-grade essays nearly perfectly. Simple prompting also evaded them [S65] (tier 2). The detectors tested date from 2023, so the specific rates may be outdated; the bias mechanism (low lexical diversity read as machine text) is the durable finding.
- **Hiring-manager attitudes.** Marketing surveys disagree on the size of the effect: 19.6% of 600 US hiring managers would reject an AI-generated resume or cover letter [S68], versus a headline figure of 49% from another survey with unclear wording [S69]. Both are tier 5 and are not weighted heavily.

Verdict: the risk is human perception of generic, AI-flavored writing, not machine detection. Confidence: medium.

### A6. Length and format

- **ATS page penalties.** No reliable source found that any ATS scores or penalizes page count. The documented limits are file sizes in megabytes [S1, S3]. Confidence: medium.
- **Official guidance.** Google: "We don't have a length requirement, but concision and precision are key" [S78] (tier 1, republished by Bright Network). Google's Kyle Ewing told Fortune in 2020 that "the number of pages doesn't matter anymore" because resumes are read on screen [S79] (tier 3, possibly outdated).
- **Human preference.** In a 2018 ResumeGo simulation with 482 hiring professionals, two-page resumes were preferred over one-page resumes, by 1.4x at entry level and 2.9x for managerial roles, with longer reading times for two pages [S71, S72, S73]. Tier 5 study reported by tier 3 and 4 press, possibly outdated, and run with a small set of resumes rather than a real queue.
- **Three pages.** No reliable source found showing ATS harm. Human-attention evidence argues against it unless the third page carries unique, relevant evidence.

Confidence: medium that two pages suits a senior individual contributor with 15+ years of experience; low on any precise effect size.

## Section B: Getting noticed by humans

### B7. Reading behavior

| Study | Method | Finding | Weaknesses | Tier |
|---|---|---|---|---|
| TheLadders eye-tracking, 2012 [S74] | 30 recruiters over 10 weeks; eye tracking plus timing | About 6 seconds for the initial fit / no-fit decision | Vendor-run, not peer-reviewed, small sample | 3 |
| TheLadders update, 2018 [S75, S76] | Timed stack review, then lab eye tracking | 7.4 seconds average; attention concentrated on current and previous title and company, dates, and education | Sample size not disclosed | 3 |
| Wonsulting, 2025 [S77] | Two recruiters wearing eye trackers | Under 10 seconds; F-pattern scanning | Two participants; coaching vendor | 5 |

Interpretation: the exact seconds are unreliable, but the pattern is consistent across studies: the top third of page one dominates, and title, employer, and dates are read first. That lines up with Greenhouse's emphasis on clean title and company fields [S1]. Confidence: medium on the pattern, low on the number.

### B8. Big-tech guidance

| Company | Official (tier 1) | Other sources |
|---|---|---|
| Google | Align skills and experience to the job description, tie work to the role's qualifications, include data, and write bullets as "accomplished [X] as measured by [Y], by doing [Z]". No length requirement [S78]. The careers portal parser may miss fields, and candidates should correct them [S3] | The X-Y-Z formula originated in Laszlo Bock's personal LinkedIn post (2014) while he was Google's SVP of People Operations [S80] (tier 4, first-hand, possibly outdated). Also repeated in press [S81], in a Google recruiter interview relayed by a career site [S82] (tier 4), and by tier-5 vendors [S88] |
| Amazon | Amazon publishes 16 Leadership Principles, from Customer Obsession to Success and Scale Bring Broad Responsibility; the official page does not connect them to resumes or applications [S98]. An Amazon manager recommends the STAR method and focusing on "I" rather than "we". This is interview guidance, not resume guidance [S83] | Advice to embed Leadership Principles in resumes comes from recruiters and vendors [S84] (tier 4), not from Amazon |
| Meta, Apple, Microsoft, Netflix | No reliable source found | Not used |

### B9. Non-FAANG tech

No reliable source with screening data specific to startups, mid-size SaaS, or hardware companies was found, and no source quantifying referral weight was gathered. What the evidence does support: growth-stage companies disproportionately run Greenhouse and Ashby [S45, S46, S48], which use criteria-calibrated or per-criterion AI review [S12, S30]. Large enterprise and hardware companies skew toward Workday [S45], whose questionnaires support disqualification [S22, S23].

### B10. Senior product manager specifics

No tier-1 or tier-2 source specific to senior PM resumes was found. Evidence that applies:

- quantified outcomes, from Google's "include data" guidance and the X-Y-Z formula [S78, S80];
- first-person ownership language, from Amazon's interview guidance [S83];
- full, unabbreviated titles and company names with legal identifiers, because parsers misread abbreviations [S1];
- a requirement-by-requirement evidence trail, because Workday Fit & Gap and Ashby both judge each qualification separately and cite the supporting resume section [S28, S30].

Reasoned recommendations built on this evidence are in `resume-fit-guidance.md`.

### B11. Myths

See the myths vs evidence table below.

## Myths vs evidence

| Claim | Origin | What the evidence shows | Verdict |
|---|---|---|---|
| "75% of resumes are rejected by ATS" | Attributed to 2012 marketing material from Preptel, a resume-optimization company that shut down in 2013; no published method [S86, S97] (tier 4 and 5 only; origin detail low-medium confidence) | Vendors document rule-based auto-reject on application answers and assistive AI ranking [S12, S15, S21]. A small 2025 recruiter interview study reports 92% do not auto-reject on resume content [S97] (weak). No study supports 75% | Myth |
| "Hidden Workers proves ATS rejects most qualified candidates" | Fuller, Raman, Sage-Gavin, Hines, HBS and Accenture, September 2021 [S85] | 88% of employers agree qualified high-skill candidates are vetted out for not matching exact criteria (94% for middle-skill). More than 90% use their recruiting systems to filter or rank candidates. The report estimates over 27 million hidden workers in the US. It surveyed 8,720 workers and 2,275 executives; it measures employer perception, not a rejection rate, and predates LLM ranking | Partly true, often overstated |
| "ATS cannot read PDFs" | Older parser limitations; tier-5 folklore | Greenhouse and Google accept .pdf; image-only files fail [S1, S3, S4] | Myth for text PDFs; true for scanned PDFs |
| "White-font keyword stuffing works" | Practitioner folklore | No reliable source found showing it improves ranking. Hidden text appears in the parsed text a recruiter sees (inference), and synonym and term repetition does not stack in Greenhouse scoring [S12] | Unsupported; high reputational risk |
| "Recruiters spend 6 seconds" | TheLadders 2012 and 2018 [S74, S75] | Vendor studies with thin methods; the pattern is plausible, the number is not reliable | Partly supported |
| "Em dashes and curly quotes break ATS" | Resume-tool blogs | No tier-1 or tier-2 source found; a single-resume extraction test found they did not break [S93] | Unsupported |
| "One page only" | Career-advice tradition | Google sets no length requirement [S78]; two pages preferred for experienced roles [S71] | Myth for senior candidates |
| "ATS auto-detects AI-written resumes" | Vendor marketing and surveys | No native text detector documented (Greenhouse checked) [S18, S19]; detectors averaged a 61.22% false-positive rate on non-native essays [S65] | Unsupported |
| "AI screeners auto-reject you" | Media coverage; Mobley v. Workday | AI scoring is documented as assistive [S12, S14, S35, S36]; auto-reject comes from recruiter rules [S15, S21]; Mobley has no merits ruling [S61] | Partly true for rules, unsupported for AI |
| "Keyword density or match percentage determines ranking" | Tier-5 ATS-score checkers | Documented scoring checks requirements individually or by weighted criteria, collapses synonyms, and boosts recent evidence [S12, S28, S29, S33] | Unsupported as stated |

## Local tests and unsourced inputs

### L1. Generated-resume extraction round trip (2026-10-03)

Purpose: check what a resume built the way `render_docx.py` builds it looks like after PDF export and text extraction.

Method: python-docx default template; Normal style set to Calibri 11 pt (LibreOffice substitutes a metric-compatible font when Calibri is absent; the substitution was not inspected); a page header containing an email address; one heading made with manual bold at 13 pt and one made with Word's "Heading 1" style; two "List Bullet" paragraphs containing "efficient", "office", and "final" (ligature candidates), an em dash, and curly quotes. Exported with `soffice --headless --convert-to pdf`; text extracted with `pdftotext` (poppler); structure checked with `pdfinfo`.

Results:
- Bullet glyph extracted as U+F0B7 (Unicode private-use area, Symbol font).
- Em dash (U+2014) and curly quotes (U+201C, U+201D) extracted intact.
- No ligature characters (for example U+FB01) appeared.
- Header text was extracted, at the top of the page.
- `pdfinfo` reported the PDF as tagged.

Limits: one document, one export engine, one open-source extractor. Microsoft Word's own PDF export and commercial ATS parsers were not tested, and the .docx file itself was not run through an extractor. In a .docx, list bullet glyphs live in the numbering definitions rather than in paragraph text (an inference from the Office Open XML structure, not tested here).

### U1. Technical briefing on document generation (unsourced)

`archive/technical_briefing_ats_optimized_document_generation.md` (added 2026-10-03; author and sources not stated) proposes formatting rules for .docx and PDF output. It cites nothing, so none of its claims is used as evidence. Its testable points are tracked as hypotheses in `resume-fit-guidance.md`, with L1 results where they apply. One claim was contradicted by L1: that standard word-processor bullets avoid corrupt substitution characters.

## Caveats and open gaps

- Market-share figures come from tier-5 vendor datasets with described but self-selected samples.
- Parsing-engine licensing is confirmed only for SAP SuccessFactors and Bullhorn (Textkernel).
- Scoring mechanics are undocumented for iCIMS, Lever, SmartRecruiters, and Oracle Taleo, and Eightfold does not publish its weights.
- Workday's August 2026 grading logic is opt-in and rolled out first through a pilot, so employers may still run the older, undocumented logic.
- Vendor statements that AI is "assistive" describe product design, not every employer's configuration or how recruiters actually use rankings.
- Several human-behavior sources (TheLadders 2012 and 2018, ResumeGo 2018, Bock 2014, Fortune 2020) predate 2024 and may be outdated.
- No official resume guidance from Meta, Apple, Microsoft, or Netflix was found.
- Sources not marked "re-checked" were carried from the automated research pass and were not individually re-opened.
- S92, S95, and S96 are preprints without peer review. S90 and S93 are vendor-published data.
- L1 is a single local test in one environment and is reported as such, not as a tier-ranked source.
- Claims in the two parallel reports reviewed in the third pass were not adopted unless their sources were opened and confirmed. Rejected claims include vector search having replaced keyword matching across ATS platforms, regulation mandating human review in NYC, and recruiters rejecting specific buzzwords.

## Bibliography

All sources accessed 2026-10-03. "Re-checked" means the source was re-opened and its cited content confirmed during the manual pass. "Undated" means no publication or update date was visible.

| ID | Tier | Publisher or author | Title | Published | URL | Notes |
|---|---|---|---|---|---|---|
| S1 | 1 | Greenhouse Support | Unsuccessful resume parse | Updated 2026-03-02 | https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse | |
| S2 | 1 | Greenhouse Support | Maildrop | Undated | https://support.greenhouse.io/hc/en-us/articles/201990630-Maildrop | |
| S3 | 1 | Google Careers Help | Resume upload and application help (answer 6095391) | Undated | https://support.google.com/googlecareers/answer/6095391?hl=en | |
| S4 | 1 | Textkernel | Resume Parser API (Tx Platform v9) | Undated | https://developer.textkernel.com/tx-platform/v9/resume-parser/api/ | |
| S5 | 1 | Textkernel | Parser documentation | Undated | https://developer.textkernel.com/Parser/master/ | |
| S6 | 1 | Textkernel | LLM Parser overview | Undated | https://developer.textkernel.com/tx-platform/v9/resume-parser/overview/llm-parser/ | |
| S7 | 1 | Textkernel | About Textkernel | Undated | https://www.textkernel.com/about-textkernel/ | |
| S8 | 1 | SAP Help Portal | Working with Resume Parsing (SuccessFactors Recruiting) | Undated | https://help.sap.com/docs/SAP_SUCCESSFACTORS_RECRUITING/8477193265ea4172a1dda118505ca631/07b6d03076a149b78f4f7a615e3025fd.html | |
| S9 | 1 | Bullhorn Knowledge Base | Updates to Resume/CV Parsing in Bullhorn ATS | Undated | https://kb.bullhorn.com/ats/Content/BHATS/Topics/parsingUpdates.htm | |
| S10 | 1 | Daxtra | Resume/CV parsing | Undated | https://www.daxtra.com/resume-cv-parsing/ | Vendor |
| S11 | 1 | Greenhouse Support | Resume parsing with non-English languages | Undated | https://support.greenhouse.io/hc/en-us/articles/205019689-Resume-parsing-with-non-English-languages | |
| S12 | 1 | Greenhouse Support | Talent Matching FAQ | Updated 2026-09-03 | https://support.greenhouse.io/hc/en-us/articles/41131886674075-Talent-Matching-FAQ | Re-checked |
| S13 | 1 | Greenhouse Support | Operational readiness guide: Talent Matching policy | Updated 2026-08-13 | https://support.greenhouse.io/hc/en-us/articles/44682413339675-Operational-readiness-guide-Talent-Matching-policy | Re-checked |
| S14 | 1 | Greenhouse Support | Talent Matching Data Processing FAQ | Undated | https://support.greenhouse.io/hc/en-us/articles/41131616864283-Talent-Matching-Data-Processing-FAQ | |
| S15 | 1 | Greenhouse Support | Application rules overview | Undated | https://support.greenhouse.io/hc/en-us/articles/203105595-Application-rules-overview | |
| S16 | 1 | Greenhouse Support | Auto-Reject for prospect post | Undated | https://support.greenhouse.io/hc/en-us/articles/360029081512-Auto-Reject-for-prospect-post | |
| S17 | 1 | Greenhouse (MyGreenhouse blog) | What really happens after you apply for a job | Undated | https://my.greenhouse.com/blogs/what-really-happens-after-you-apply-for-a-job | Vendor blog |
| S18 | 1 | Greenhouse Support | Fraud Detection | Undated | https://support.greenhouse.io/hc/en-us/articles/42738009117467-Fraud-Detection | |
| S19 | 1 | Greenhouse Support | Real Talent instructions | Undated | https://support.greenhouse.io/hc/en-us/articles/41452459037467-Real-Talent-instructions | |
| S20 | 1 | Greenhouse via PR Newswire | Greenhouse Real Talent launches to fix overwhelming candidate pipelines while combatting fraud and spam in hiring | 2025-06-03 | https://www.prnewswire.com/news-releases/greenhouse-real-talent-launches-to-fix-overwhelming-candidate-pipelines-while-combatting-fraud-and-spam-in-hiring-302472057.html | |
| S21 | 1 | Lever Help Center | How do I set up auto-screening questions? | Undated | https://help.lever.co/hc/en-us/articles/360038711551-How-do-I-set-up-auto-screening-questions- | |
| S22 | 1 | Workday Education | Recruiting for Administrators: job requisition components | Undated | https://doc.workday.com/workday-education/en-us/course-manuals/recruiting-for-administrators/job-requisition-components.html | |
| S23 | 1 | Workday Education | Recruiting for Administrators: recruiting subprocesses | Undated | https://doc.workday.com/workday-education/en-us/course-manuals/recruiting-for-administrators/recruiting-subprocesses.html | |
| S24 | 1 | Workday Education | Recruiting for Administrators: prospects and candidates | Undated | https://doc.workday.com/workday-education/en-us/course-manuals/recruiting-for-administrators/prospects-and-candidates.html | |
| S25 | 1 | Workday HiredScore | Concept: HiredScore Grades | 2023-06-23 | https://doc.workday.com/hiredscore/en-us/workday-hiredscore/recruiter-productivity-/concept--hiredscore-grades.html | Re-checked |
| S26 | 1 | Workday HiredScore | Reference: Candidate Grades | 2023-06-23 (per research run) | https://doc.workday.com/hiredscore/en-us/workday-hiredscore/recruiter-productivity-/reference--candidate-grades.html | |
| S27 | 1 | Workday HiredScore | Concept: Spotlight | 2023-06-23 | https://doc.workday.com/hiredscore/en-us/workday-hiredscore/recruiter-productivity-/concept--spotlight.html | Re-checked |
| S28 | 1 | Workday HiredScore | Concept: Fit & Gap | Undated | https://doc.workday.com/hiredscore/en-us/workday-hiredscore/recruiter-productivity-/concept--fit---gap.html | Re-checked |
| S29 | 1 | Workday HiredScore | Release notes: Wednesday 5th August (2026) | 2026-08-05 | https://doc.workday.com/hiredscore/en-us/workday-hiredscore/hiredscore-release-notes/2026/august/wednesday--5th-august.html | Re-checked |
| S30 | 1 | Ashby | AI-Assisted Application Review | Undated | https://docs.ashbyhq.com/ai-assisted-application-review | Re-checked |
| S31 | 1 | Ashby | Automatically generate AI job criteria (product update) | 2024-10-01 | https://www.ashbyhq.com/product-updates/automatically-generate-ai-job-criteria | Re-checked |
| S32 | 2 | FairNow for Ashby | Bias audit of Ashby criteria evaluation (NYC LL144) | 2024-08-23 | https://www.ashbyhq.com/downloadables/ashby-bias-audit-08-2024.pdf | Re-checked; independent audit |
| S33 | 1 | Textkernel | Search & Match: Matching, Scoring | Undated | https://developer.textkernel.com/SearchMatch/master/Matching/Scoring/ | Re-checked |
| S34 | 1 | Textkernel | Search & Match v2 overview (Tx Platform v10) | Undated | https://developer.textkernel.com/tx-platform/v10/search-match-v2/overview/ | Re-checked |
| S35 | 1 | Eightfold AI | Eightfold Matching Model | Updated 2025-03-21 | https://eightfold.ai/nyc-eightfold-matching-model | Re-checked; references a bias audit dated 2026-03-06 |
| S36 | 1 | LinkedIn | AI Transparency in Hiring Solutions: Hire | Undated | https://business.linkedin.com/hire/ai-transparency/hire | Re-checked |
| S37 | 1 | iCIMS | AI recruiting, search and automation | Undated | https://icims.com/talent-cloud-recruiting/platform/ai-recruiting-search-automation | Re-checked; marketing page |
| S38 | 1 | RChilli Help Center | What are the Skill types that RChilli have or supports | Undated | https://help.rchilli.com/hc/en-us/articles/360011188594-What-are-the-Skill-types-that-RChilli-have-or-supports | Re-checked |
| S39 | 1 | RChilli Help Center | How Do I Know if My Resume Parsing is Correctly Capturing Skills from Job Experience | 2025-06-24 | https://help.rchilli.com/hc/en-us/articles/48254955870233-How-Do-I-Know-if-My-Resume-Parsing-is-Correctly-Capturing-Skills-from-Job-Experience | Re-checked |
| S40 | 1 | Lightcast | Open Skills FAQs | Undated | https://lightcast.io/open-skills/faqs | Re-checked |
| S41 | 1 | Affinda | Resume taxonomies | Undated | https://docs.affinda.com/resumes/taxonomies | Re-checked |
| S42 | 1 | Affinda | How to parse resumes online for free | Undated | https://www.affinda.com/blog/how-to-parse-resumes-online-for-free/ | Vendor blog |
| S43 | 1 | Affinda | NextGen resume parser launch | Undated | https://www.affinda.com/blog/nextgen-resume-parser-launch/ | Vendor blog |
| S44 | 1 | Textkernel | Parser product page | Undated | https://www.textkernel.com/products-solutions/parser/ | |
| S45 | 5 | Jobscan | Fortune 500 ATS usage report (2025) | 2025-07 | https://www.jobscan.co/blog/fortune-500-use-applicant-tracking-systems/ | Marketing; described method |
| S46 | 5 | ResumeGeni | ATS market share 2026 | 2026 | https://resumegeni.com/research/ats-market-share-2026 | Marketing |
| S47 | 3 | Mordor Intelligence | Applicant tracking system market | 2026 | https://www.mordorintelligence.com/industry-reports/applicant-tracking-system-market | |
| S48 | 4 | Relio Engine | Choosing your first ATS | Undated | https://relioengine.com/consulting/blog/choosing-your-first-ats | Relays vendor and Crunchbase figures |
| S49 | 4 | Onrec | Textkernel introduces LLM Parser | Undated | https://www.onrec.com/news/partnerships/textkernel-introduces-llm-parser-a-leap-forward-in-resume-parsing-and-recruitment | |
| S50 | 3 | DLA Piper | Critical audit of NYC AI hiring law signals increased risk for employers | 2026-01 | https://www.dlapiper.com/en-us/insights/publications/2026/01/critical-audit-of-nyc-ai-hiring-law-signals-increased-risk-for-employers | Summarizes the NY State Comptroller audit of 2025-12-02 |
| S51 | 4 | Warden AI | HR tech compliance: NYC Local Law 144 | Undated | https://www.warden-ai.com/resources/hr-tech-compliance-nyc-local-law-144 | Audit vendor |
| S52 | 3 | Kinstellar | The AI Act after the Digital Omnibus | Undated | https://www.kinstellar.com/news-and-insights/detail/4619/the-ai-act-after-the-digital-omnibus-simplified-rules-delayed-deadlines-but-can-compliance-wait | |
| S53 | 3 | Jones Walker | Yes, August 2 still matters: the EU approved a high-risk AI delay | Undated | https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html?id=102nbon | |
| S54 | 3 | Seyfarth Shaw | Colorado enacts artificial intelligence replacement law | 2026 (exact date not shown) | https://www.seyfarth.com/news-insights/colorado-enacts-artificial-intelligence-replacement-law.html | |
| S55 | 3 | Finnegan | Colorado replaces landmark AI Act: an overview of the new SB 26-189 framework | Undated | https://www.finnegan.com/en/insights/articles/colorado-replaces-landmark-ai-act-an-overview-of-the-new-sb-26-189-framework.html | |
| S56 | 3 | Lathrop GPM | Colorado enacts new law regulating automated decision-making technology | Undated | https://www.lathropgpm.com/insights/colorado-enacts-new-law-regulating-automated-decision-making-technology/ | |
| S57 | 3 | Buchalter | Colorado rewrites its AI law: what employers must know about SB 26-189 | Undated | https://www.buchalter.com/insights/colorado-rewrites-its-ai-law-what-employers-must-know-about-sb-26-189/ | |
| S58 | 3 | The Employer Report | AI regulation on hold in Colorado, but employer risk isn't | 2026-05 | https://www.theemployerreport.com/2026/05/ai-regulation-on-hold-in-colorado-but-employer-risk-isnt/ | |
| S59 | 4 | Rocky Mountain Employers Blog | Colorado rewrites its primary AI law | 2026-06-04 | https://www.rockymountainemployersblog.com/blog/2026/6/4/colorado-rewrites-its-primary-ai-law-what-employers-need-to-know-before-2027 | |
| S60 | 3 | Seyfarth Shaw | AI legal roundup: Colorado postpones, California finalizes, Illinois disclosure law | Undated | https://www.seyfarth.com/news-insights/artificial-intelligence-legal-roundup-colorado-postpones-implementation-of-ai-law-as-california-finalizes-new-employment-discrimination-regulations-and-illinois-disclosure-law-set-to-take-effect.html | |
| S61 | 3 | Civil Rights Litigation Clearinghouse | Mobley v. Workday | Undated | https://clearinghouse.net/case/44074/ | |
| S62 | 3 | CDF Labor Law | Federal court grants preliminary certification in landmark AI hiring bias case | 2025 (exact date not shown) | https://www.cdflaborlaw.com/blog/federal-court-grants-preliminary-certification-in-landmark-ai-hiring-bias-case | |
| S63 | 4 | Hall and Hall Law | Mobley v. Workday: the AI vendor as AI agent | Undated | https://hh-law.com/blogs/employment-labor-law/mobley-v-workday-the-ai-vendor-as-ai-agent-creating-potential-new-liabilities/ | |
| S64 | 3 | CBS News (via Yahoo News) | Workday discriminatory hiring tech lawsuit coverage | Undated | https://www.yahoo.com/news/workday-discriminatory-hiring-tech-prevented-093053070.html | |
| S65 | 2 | Liang, Yuksekgonul, Mao, Wu, Zou (Patterns) | GPT detectors are biased against non-native English writers | 2023 (arXiv 2023-04-06) | https://arxiv.org/html/2304.02819v3 | Re-checked (7 detectors, 91 TOEFL essays, 61.22% average false-positive rate); peer-reviewed; possibly outdated |
| S66 | 5 | Zapier | Detect AI in new Greenhouse candidate applications with GPTZero | Undated | https://zapier.com/apps/google-sheets/integrations/greenhouse/255560563/detect-ai-in-new-greenhouse-candidate-applications-with-gptzero-and-create-google-sheets-rows | Marketing |
| S67 | 5 | Brainner | Brainner for Greenhouse | Undated | https://www.brainner.ai/greenhouse | Marketing |
| S68 | 5 | NRCA (relaying a TopResume survey) | Hiring managers sometimes reject applicants who use AI | 2025-09-16 | https://www.nrca.net/RoofingNews/hiring-managers-sometimes-reject-applicants-who-use-ai.9-16-2025.12931/details/story | Underlying survey is marketing |
| S69 | 5 | Resume.io | Resume rejections survey | 2025-01 | https://resume.io/blog/resume-rejections | Marketing |
| S71 | 3 | CNBC | Hiring managers prefer candidates with two-page resumes (ResumeGo study) | 2018-12-19 | https://www.cnbc.com/2018/12/19/resumego-hiring-managers-prefer-candidates-with-two-page-resumes.html | Underlying study tier 5; possibly outdated |
| S72 | 4 | ERE | One or two page resumes | Undated | https://www.ere.net/articles/one-or-two-page-resumes-best | |
| S73 | 4 | Dice | Two-page or one-page resume | Undated | https://www.dice.com/career-advice/two-page-one-page-resume-okay-tech-recruiters | |
| S74 | 3 | TheLadders (hosted by Boston University) | Eye-tracking study | 2012 | https://www.bu.edu/com/files/2018/10/TheLadders-EyeTracking-StudyC2.pdf | Vendor-run; possibly outdated |
| S75 | 3 | TheLadders via PR Newswire | Ladders updates popular recruiter eye-tracking study | 2018 | https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html | Vendor-run; possibly outdated |
| S76 | 4 | TheLadders | Is it true that recruiters reject a resume in six seconds? | Undated | https://www.theladders.com/career-advice/is-it-true-that-recruiters-reject-a-resume-in-six-seconds | |
| S77 | 5 | Wonsulting | Hidden eye tracker: how recruiters actually read resumes | 2025 | https://www.wonsulting.com/job-search-hub/hidden-eye-tracker-how-recruiters-actually-read-resumes | Marketing |
| S78 | 1 | Google (republished by Bright Network) | Google: how we hire | Undated | https://www.brightnetwork.co.uk/employer-advice/google/google-how-we-hire/ | Re-checked; Google-authored content |
| S79 | 3 | Fortune | Resume tips: how to make a resume that gets noticed by companies like Google | 2020-02-14 | https://fortune.com/2020/02/14/how-to-make-a-resume-get-hired-at-goo | Re-checked; possibly outdated |
| S80 | 4 | Laszlo Bock (LinkedIn) | My personal formula for a winning resume | 2014-09-29 | https://www.linkedin.com/pulse/20140929001534-24454816-my-personal-formula-for-a-better-resume | First-hand; possibly outdated |
| S81 | 3 | Inc. (Bill Murphy Jr.) | Google recruiters say these 5 resume tips, including the X-Y-Z formula, will improve your odds | 2019 (per research run) | https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html | Possibly outdated |
| S82 | 4 | Europe Language Jobs | How to get a job at Google | Undated | https://www.europelanguagejobs.com/blog/how-to-get-a-job-at-google | |
| S83 | 1 | About Amazon | Amazon leadership principles interview guidance | Undated | https://www.aboutamazon.com/news/workplace/amazon-leadership-principles-interview | |
| S84 | 4 | IGotAnOffer | Amazon resume examples and tips | Undated | https://igotanoffer.com/en/advice/amazon-resume-examples-tips | |
| S85 | 2 | Fuller, Raman, Sage-Gavin, Hines (HBS Project on Managing the Future of Work and Accenture) | Hidden Workers: Untapped Talent | 2021-09 (updated 2021-10-04) | https://www.hbs.edu/managing-the-future-of-work/Documents/research/hiddenworkers09032021.pdf | Re-checked (pp. 2, 3, 15); possibly outdated |
| S86 | 5 | UnchartedCareer | The "75% of resumes are auto-rejected" myth traced to its source | Undated | https://unchartedcareer.com/blog/the-75-of-resumes-are-auto-rejected-myth-traced-to-its-source | Marketing; only source for the origin story |
| S87 | 5 | ResumeOptimizerPro | Workday resume format | Undated | https://resumeoptimizerpro.com/blog/workday-resume-format | Marketing |
| S88 | 5 | Teal | XYZ resume formula | Undated | https://www.tealhq.com/post/xyz-resume | Marketing |
| S89 | 1 | SAP News | SAP completes SmartRecruiters acquisition | 2025-09-11 | https://news.sap.com/2025/09/sap-completes-smartrecruiters-acquisition/ | Re-checked |
| S90 | 5 | Pin | 2026 ATS market share report: what recruiting teams actually use | 2026-07-20 (updated 2026-09-27) | https://www.pin.com/blog/ats-market-share-report/ | Re-checked; AI sourcing vendor; relays analyst market-size estimates |
| S91 | 3 | Husch Blackwell | AI and workplace discrimination: what employers need to know after the EEOC and DOL rollbacks | 2025-02-07 | https://www.huschblackwell.com/newsandinsights/ai-and-workplace-discrimination-what-employers-need-to-know-after-the-eeoc-and-dol-rollbacks | Re-checked |
| S92 | 2 | ManpowerGroup Services India and IIT Hyderabad (arXiv) | Semantic candidate-job matching: a comparative evaluation of dense embedding models in hybrid retrieval | 2026-09-22 | https://arxiv.org/html/2609.23307v1 | Re-checked; preprint |
| S93 | 5 | ATSVerification (Tanzeel Labs) | ATS parsing benchmark 2026 | 2026-06-30 | https://atsverification.com/blog/ats-parsing-benchmark-2026/ | Re-checked; sells resume-scanning tools; one resume, six layouts |
| S94 | 3 | SHRM (Roy Maurer) | Workday's ATS is the "top choice" of the Fortune 500 | 2019-08-06 | https://shrm.org/topics-tools/news/talent-acquisition/workdays-ats-top-choice-fortune-500 | Re-checked; relays Ongig data; outdated |
| S95 | 2 | arXiv | When names change verdicts: intervention consistency reveals systematic bias in LLM decision-making (ICE-Guard) | 2026-03 | https://arxiv.org/abs/2603.18530 | Re-checked (abstract); preprint |
| S96 | 2 | Hoffstedde, Hirota, Kanna, Kotani, Kumar, Trovato, Tan (arXiv) | Gender bias in LLM hiring decisions: evidence from a Japanese context and evaluation of mitigation strategies | 2026-06-17 | https://arxiv.org/abs/2606.18649 | Re-checked (abstract); preprint |
| S97 | 4 | Ronn Torossian | Resume rejection myth debunked: ATS data and real reasons | Undated | https://ronntorossian.com/resume-rejection-myth-debunked | Re-checked; relays Enhancv 2025 study and an ApplyMate 2026 review |
| S98 | 1 | Amazon | Leadership Principles | Undated | https://www.amazon.jobs/content/en/our-workplace/leadership-principles | Re-checked |
