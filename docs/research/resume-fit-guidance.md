# resume-fit Guidance: Format, Content, Application, and Rule Audit (2026)

Status: advice and action. This file turns the evidence in `ats-evidence-2026.md` into rules for building and submitting a resume, audits the `resume-fit` skill against them, and lists proposed changes. It changes when the skill changes; the evidence file changes only when the research is redone. No code, contract, or schema in `.claude/skills/resume-fit/` has been changed, Proposed changes are tracked in `TODO.md` (see section 6).

Prepared: 2026-10-03, split from the original combined report (its index is archived at `archive/ats-and-resume-screening-2026.md`).

## How to read this file

Bracketed IDs refer to `ats-evidence-2026.md`: [S#] is a bibliography source, [L#] is a local test run for this project, and [U1] is the unsourced technical briefing on document generation. Every rule carries one of four status labels:

| Status | Meaning |
|---|---|
| Evidence-backed | Stated by tier-1 or tier-2 sources, or consistent across weaker ones |
| Tested locally | Observed in a project test (L-numbered); limited to that environment |
| Hypothesis | Plausible and cheap to adopt, but undocumented by any parser vendor and untested |
| Style choice | A house preference with no ATS basis; keep or drop on taste |
| Practitioner consensus | Repeated across career-advice sources (tier 4 or 5) but never tested; adopt as convention, do not cite as evidence |
| Project rule | A decision made for this project; it follows from the no-fabrication and voice invariants, not from outside evidence |

## 1. Document format rules

| Rule | Status | Basis |
|---|---|---|
| Single column, top to bottom | Evidence-backed | Greenhouse lists columns as a parse breaker [S1]; a direct test showed a two-column layout scrambling reading order [S93] |
| No tables, text boxes, graphics, or word art | Evidence-backed | Greenhouse [S1]. U1's claim that text boxes are skipped or appended out of order fits this but is not separately documented |
| Name and contact details in the body, never only in a header, footer, or text box | Evidence-backed | Greenhouse [S1]. In L1 the PDF header text was extracted, and in [S93] it was extracted three times, so the failure is unreliable placement rather than guaranteed loss |
| Standard section headings (Summary, Experience, Education, Skills) and one consistent entry and date format | Evidence-backed | Greenhouse [S1]; nonstandard headings flagged in [S93] |
| Full job titles and company names with legal identifiers where truthful | Evidence-backed | Greenhouse: abbreviated titles and names without Inc. or LLC parse poorly [S1] |
| File under 2 MB | Evidence-backed | Google 2 MB upload cap [S3]; Greenhouse 2.5 MB parse limit [S1] |
| .docx or text-based PDF; never a scanned or image-only file | Evidence-backed | Both formats accepted by Greenhouse and Google [S1, S3]; image-only files fail [S1, S4] |
| In PDF output, avoid the Symbol-font bullet | Tested locally | python-docx's default "List Bullet" glyph extracted as private-use U+F0B7 after LibreOffice export [L1]. Use a plain U+2022 bullet character or a hyphen, then confirm with an extraction check. Not tested with Word's own export |
| Export to PDF from the source application; never "Print to PDF" | Hypothesis | U1. Export preserves links and structure tags (L1 export was tagged); no parser vendor documents reading tags. Cheap to adopt. For an open-source path, LibreOffice headless export worked in L1 |
| Use real heading styles (Word "Heading 1" or "Heading 2") rather than manual bold and size | Hypothesis | U1. No vendor documents relying on them. `render_docx.py` currently builds headings from manual bold and font size. Cost: restyle the built-in heading style, which defaults to a colored font |
| Show full URLs as visible text | Hypothesis | Reasoned correction to U1, which recommended native hyperlinks because parsers supposedly cannot detect plain URLs. Parsers routinely extract URLs from text; the real risk is link text such as "LinkedIn" hiding the address from the extracted text |
| Fonts: any common sans or serif face | No rule needed | No evidence that typeface affects parsing; L1 showed no ligature substitution. U1's ligature concern is not supported |
| No em dashes, en dashes, or curly quotes | Style choice | No tier-1 or tier-2 source treats them as parse failures; [S93] and [L1] both extracted them intact. Keep as house style if wanted |
| No emoji or icon fonts | Evidence-backed (weak) | Graphics and decorative elements are documented failure points [S1]; emoji themselves are not specifically documented |
| Two pages for a senior candidate; three only when page three adds unique evidence | Evidence-backed | No ATS page penalty found; Google sets no length requirement but stresses concision [S78]; two pages preferred for experienced roles [S71] |
| Invisible tables to align content in PDF | Rejected | Proposed by U1; contradicts Greenhouse [S1] and U1's own .docx rule |

## 2. Content rules

| Rule | Status | Basis |
|---|---|---|
| Write bullets as accomplishment, measure, method (Google X-Y-Z) | Evidence-backed | Google "How we hire" [S78]; Bock [S80] |
| Put each required skill inside a dated, recent role, not only in a Skills list | Evidence-backed (mechanism) | Textkernel weights recent titles and skills in recent positions [S33]; parsers record months of use and last-used date per skill [S39] |
| Leave an evidence trail for each stated requirement | Evidence-backed | Workday Fit & Gap and Ashby judge each qualification separately and cite the supporting resume section [S28, S30] |
| Do not repeat synonyms to inflate matches | Evidence-backed | Greenhouse maps many terms to one calibrated skill [S12] |
| Show soft skills through outcomes (scope, influence, communication results), not adjective lists | Inference | Vendors steer scoring away from soft-skill criteria [S13, S30]; LLM evaluators can infer soft qualifications from described work [S28, S36]; see evidence file A3.1 |
| Put the current title, employer, dates, and location in the top third of page one | Evidence-backed (pattern) | Reading-behavior studies agree on attention to title, employer, and dates first, though not on exact seconds [S74, S75] |
| Lead each role with scope (users, revenue, platform reach, team size) | Reasoned | Builds on the quantified-outcome guidance [S78, S80]; no senior-PM-specific source found |
| Present independent consulting as a titled role with a named entity and client outcomes | Reasoned | Builds on the title and company-identifier parsing issues [S1] |
| For startups, foreground zero-to-one scope and shipping speed; for hardware companies, cross-functional hardware and software delivery | Reasoned | No screening data by company type was found (evidence file B9) |
| Amazon Leadership Principles: demonstrate them through evidence; do not treat them as an official resume requirement | Evidence-backed | Amazon's page lists 16 principles and does not connect them to resumes [S98]; STAR and "I" language are interview guidance [S83] |

## 3. Application rules

| Rule | Status | Basis |
|---|---|---|
| Before applying, check that the resume agrees with planned answers to likely knockout questions (location, relocation, work authorization, years of experience, salary) | Evidence-backed (mechanism) | Recruiter-configured auto-reject and disqualification on application answers [S15, S16, S21, S22, S23] |
| Where an employer offers an AI opt-out, it routes the application to manual review | Evidence-backed | Greenhouse [S12, S13] |
| Check the employer's autofill preview after upload and correct missed fields | Evidence-backed | Google asks candidates to correct parser misses [S3] |
| Treat the header location as a targeting setting: for on-site or hybrid targets, state the location the candidate will actually work from, and make sure no other city on the page (such as the most recent role's) is the one the parser picks up | Tested locally | On Eightfold's Netflix career site, the resume's location set the job pool: a Kettering header returned only remote roles, and with no header location the parser used the most recent role's city [L2]. A relocation phrase had no visible effect. One platform; Textkernel also documents location as a weighted criterion that drops out for remote jobs [S33, S34] |
| Expect the vocabulary in a resume tuned for one target to carry over to every other submission | Tested locally | On the same site, heavy AI and ML wording returned engineering and research roles to a PM, while PM-flavored wording returned only product roles [L2]. Keep one variant per target family rather than reusing a tuned resume |

## 4. Verifying a resume without replicating an ATS

Ranked by how close each method is to what a real employer sees:

1. **The employer's own apply-flow autofill.** Workday, Greenhouse, Lever, and Google portals parse the upload and prefill fields. Google explicitly asks candidates to correct missed fields [S3]. A mismatched field is direct evidence of what the recruiter's record will show. Practitioner technique (tier 4, reasoned): use a throwaway account on a large Workday employer's site and stop at the autofill step without submitting.
2. **Textkernel trial.** Textkernel offers a free trial with demo and API access, including an LLM parser mode [S6, S44] (tier 1). Because SuccessFactors and Bullhorn use Textkernel [S8, S9], this is the closest available enterprise parser. Requires sign-up.
3. **Affinda demo.** Affinda describes a free trial path with initial credits [S42, S43] (tier 1, vendor). Current terms are unclear, and its API is proprietary and metered.
4. **Local extraction round trip.** Export the resume, extract the text with an open-source extractor such as poppler's `pdftotext`, and look for private-use characters, scrambled reading order, and contact details that appear only in a header. This is the procedure used in [L1]; it catches extraction problems but is not a commercial parser.
5. **Plain-text paste test.** Copy all text out of the PDF or .docx into a plain-text editor. If reading order scrambles, parsers likely will too (tier 4 practitioner method, reasoned).

Tier-5 "ATS score" checkers model keyword overlap, which is the overfitting this project has decided against. They are not parsers and should not be used as a pass/fail gate.

## 5. Rule audit of the resume-fit skill

| Rule | Current behavior | Verdict | Evidence | Recommended change |
|---|---|---|---|---|
| R1 `helpers/ats.py` | Exact-string coverage percentage of JD keywords; case-insensitive word-boundary matching; taxonomy synonyms treated as equivalent; case-sensitive short terms (Go, REST, Node, AI, ML, TS, RN) | Partly supported | Literal terms matter for recruiter search (tier 4/5). But documented AI scoring checks each requirement individually [S28, S29, S30], weights criteria [S13, S33], collapses synonyms into one skill [S12], and favors recent, dated evidence [S33, S39]. No source documents a coverage-percentage threshold | Replace the single percentage with a per-requirement verdict: split basic and preferred qualifications, flag unmet basic ones as gate risks, record where the evidence sits (recent dated role, older role, skills list only), and stop counting synonym hits as extra coverage. Keep the case-sensitive handling |
| R2 `helpers/ats_chars.py` | Flags em/en dashes, curly quotes, inline bullets, arrows, decorative symbols, and emoji as "documented ATS parsing failure points"; flags prose "&" | Mostly unsupported; emoji and decorative symbols partly supported | Graphics, word art, and letter-spacing are documented [S1]. No tier-1 or tier-2 source documents dashes, quotes, or "&" as failures. The one direct test found reports em dashes and curly quotes did not break extraction [S93] (tier 5, single resume) | Remove the "documented ATS parsing failure points" claim. Reclassify dash, quote, and arrow flags as house style (the no-dash rule can stay as a style rule). Keep emoji and icon flags as low-risk hygiene. Keep the "&" check only where the JD phrase is a plausible recruiter search term |
| R3 `helpers/render_docx.py` | .docx only; single column; Calibri 11pt; 0.6 in margins; no tables, text boxes, headers, or footers | Supported for layout; partly supported for .docx-only | Greenhouse names tables, headers, footers, columns, text boxes, and header contact details as parse breakers [S1]. A direct test reproduced reading-order scrambling from a two-column layout and repeated extraction from a page header [S93] (tier 5). .pdf and .docx are both accepted [S1, S3]. No evidence either way on font, size, or margins | Keep the layout constraints. Add a text-based PDF output, a file-size gate under 2 MB [S3], and an assertion that name and contact details render in the document body |
| R4 `helpers/length_budget.py` | Two-page default target for a senior IC; advisory warning only | Supported | No ATS page penalty found; Google sets no length requirement but stresses concision [S78]; two-page preference for experienced roles [S71] | Keep. Raise a stronger warning at three pages unless page three carries unique evidence, and check that the strongest metric sits in the top third of page one |
| R5 `contracts/screening.md` | Gate 1 "6-second" recruiter screen on headline, summary, and most recent role; Gate 2 "3-minute" hiring-manager skim; risk-averse default | Partly supported | The Ladders numbers are vendor-run with thin methods, but the attention pattern (title, employer, dates first) is consistent [S74, S75]. Hidden Workers supports a risk-averse, exact-criteria default [S85]. The simulation is itself LLM-run, and LLM evaluators show framing, authority, and gender effects [S95, S96] | Rename the gates "fast scan" and "deep read" and drop the specific seconds. Have Gate 1 check current title, employer, dates, and location in the top third. Keep the "approximation, not prediction" framing, and state LLM-evaluator bias as a known limitation |
| Missing: contact placement | Not checked | Missing | Contact details in a header, footer, or text box break parsing [S1] | Add a check |
| Missing: full titles and title alignment | Not checked | Missing | Abbreviated titles parse poorly [S1]; title is a weighted criterion [S12, S34] and is recency-boosted [S33] | Expand abbreviations ("Sr." to "Senior"); flag divergence from the JD's title family and suggest a truthful parenthetical |
| Missing: company identifiers | Not checked | Missing | Names without Inc., LLC, and similar may parse poorly [S1] | Suggest legal entity names where truthful, especially for consulting entries |
| Missing: section headings and format consistency | Not checked | Missing | Missing or inconsistent sections cause partial parses [S1]; nonstandard headings were flagged in a direct test [S93] | Enforce a heading allowlist (Summary, Experience, Education, Skills) and one date format throughout |
| Missing: file size | Not checked | Missing | 2 MB (Google) and 2.5 MB (Greenhouse parse) limits [S1, S3] | Add a size gate |
| Missing: knockout consistency | Not checked | Missing | Recruiter-configured auto-reject on application answers [S15, S16, S21, S22] | Add a pre-apply checklist covering location, relocation, work authorization, years of experience, and salary, checked against the resume |
| Missing: quantified impact | Not checked deterministically | Missing | Google's "include data" and X-Y-Z guidance [S78, S80] | Flag bullets that lack a measure or a method |
| Missing: real-parser verification | Not in workflow | Missing | Employer autofill and vendor trials are real parsers [S3, S6, S42] | Add a manual verification step and record mismatched fields |
| Missing: LinkedIn consistency, referrals | Not checked | Missing (no evidence gathered) | No reliable source found | Optional advisory, marked unverified |

## 6. Where the proposed changes went

The 14 changes proposed in the original report were reconciled with `TODO.md` on 2026-10-03, in the section "ATS evidence alignment (research 2026-10-03)". `TODO.md` is now the only list; this table records the mapping.

| Original proposal | TODO.md item |
|---|---|
| 1. Contact placement check | #16 |
| 2. Knockout consistency checklist | #24 (narrowed: location and relocation already done in #10) |
| 3. Per-requirement scoring in `ats.py` | #25 (per-requirement verdicts already exist in the gapmap, #12) |
| 4. Title and entity normalization | #17 |
| 5. PDF output and size gate | #19 (size gate) and #26 (PDF output) |
| 6. Real-parser verification step | #27 |
| 7. Evidence recency check | #25 (`evidence_location` in gapmap rows) |
| 8. Impact check | #22 (absorbs Antigravity item A3) |
| 9. Section and date consistency | #18 |
| 10. Relabel `ats_chars.py` | #20 |
| 11. Rename the screening gates | #21 |
| 12. Tune `length_budget.py` | #23 |
| 13. LinkedIn consistency and referrals | Roadmap (no evidence gathered) |
| 14. LLM-evaluator bias note | #21 |

Format rules from section 1 that became TODO items: the Symbol-font bullet and export method (#26), heading styles (#28), and visible URLs (#29).

## 7. Summary rules (added 2026-10-10)

Evidence base: thin. The project's own evidence file has nothing on summaries. The only measured data is the TheLadders eye-tracking study, which is vendor-run and from 2012 [S74, S75]; the rest is career-advice writing (tier 4 and 5) gathered on 2026-10-10 (sources listed at the end of this section; not yet in the bibliography). Rules below say which kind of basis they have.

**Decision, 2026-10-10: there is no "candidate type".** An earlier plan had a single approved statement of "who I am" anchor the summary and serve as the stable comparison for the screen's archetype read (TODO #15). It is dropped. It locked the resume to a niche taken from the WHD's record of the past (the self-ranked domain list), it had no consumer in the pipeline beyond the summary, and the archetype fields in the gapmap remain per-run diagnostics only. Direction is expressed through which true material is foregrounded (rule S6), never through a stored identity statement.

### 7.1 What a summary is, and how much it weighs

| # | Rule | Status | Basis |
|---|---|---|---|
| S1 | The summary is a claim, not evidence. It carries little weight in screening and cannot rescue bullets that fail. | Evidence-backed (mechanism); the weight is inference | First-pass attention goes to name, titles, employers, dates and education, and explanatory prose had little effect on that decision [S74, S75]. Requirement-by-requirement scoring cites the supporting resume section [S28, S30], and skills in recent dated roles are favored [S33, S39] |
| S2 | It must not displace current title, employer, dates and location from the top third of page one. | Evidence-backed (pattern) | [S74, S75]. Same rule as section 2 |
| S3 | Its role is orientation and a checkable thesis: it tells a reader who goes past the first pass what to look for, and the bullets must then prove it. | Practitioner consensus | Career-advice sources agree on purpose; no test found |
| S4 | A summary is optional. Omit it before letting it push the first page past two. | Project rule | Follows from S1 and the two-page default |

### 7.2 Content

| # | Rule | Status | Basis |
|---|---|---|---|
| S5 | Every claim in a summary traces to an approved library bullet, and that bullet traces to a WHD anchor. A claim with no bullet is removed or the bullet is written first. | Project rule | No-fabrication invariant; an unsupported claim also leaves a requirement with no evidence trail [S28, S30] |
| S6 | Direction comes from selection, not declaration. Aspirations decide which true capabilities lead and which targets are pursued. They never add a fact, a skill or a claim of experience, and they are not stored in the WHD (the WHD is the record of what happened). | Project rule | Separates the record from intent; keeps the WHD usable for any target |
| S7 | Do not tie the summary to one domain or employer type unless the target requires it. Write one summary per target family. | Project rule | Decision 2026-10-10; the candidate-type statement above failed this test |
| S8 | State the role and scope, then two or three quantified results where the WHD supports a measure. Do not invent a measure. | Practitioner consensus, plus the project's X-Y-Z rule | Sources agree on numbers and scope; the X-Y-Z rule is in section 2 [S78, S80] |
| S9 | Two to four lines. No first-person pronouns. No objective statement ("seeking a role that..."). | Practitioner consensus | Objectives are discouraged for experienced candidates in the sources gathered; length is advice only |
| S10 | Name the through-line of a mixed background by what the work had in common (the capability), not by listing industries. | Practitioner consensus | Career-change guidance in the sources gathered |
| S11 | Mirror the target's vocabulary only where it is true, once, without synonym repetition. | Evidence-backed | Greenhouse maps many terms to one calibrated skill [S12] |
| S12 | Prefer concrete scope and results to adjectives. Phrases such as "results-driven" and "detail-oriented" are weak, but they are not auto-rejected, so the rule is a writing standard, not a lint. | Practitioner consensus | Recruiter commentary; compare closed TODO A2, which found no evidence that recruiters reject specific words |
| S13 | The wording must pass the voice check against the WHD voice sample and use no dash or arrow characters (house style). | Project rule | Existing invariants in `contracts/finishing.md` |

### 7.3 How the pieces relate

```
WHD            what happened; all of it; fixed; never states direction
  |  (anchors)
bullet library approved wording of true facts; each bullet traces to an anchor; tagged by capability
  |  (selection)
master resume  curated default selection; summary slot filled by a variant
  |  (tailoring)
job resume     bullets chosen and ordered for one JD; one summary variant chosen or adapted
```

- The **job description** is the question. Each requirement should have a bullet that answers it, or be reported as an honest gap.
- **Aspirations** are a filter on which jobs to pursue and which true material leads. They are not evidence (S6).
- The **summary** is the thesis that connects them. The **bullets** are the proof. A summary claim without a bullet fails S5; a strong bullet that no summary mentions is fine.
- Tailoring starts from the master and the library, never from the previous job's resume (the compounding problem this whole design fixes).

Sources gathered 2026-10-10 (tier 4 and 5, not yet numbered in the bibliography):
- ATD, "What recruiters look at during the 6 seconds": https://www.td.org/content/atd-blog/what-recruiters-look-at-during-the-6-seconds-they-spend-on-your-resume
- Built In, "14 Tips for Writing a Stellar Product Manager Resume": https://builtin.com/articles/product-manager-resume
- Product School, "The Product Management Resume Checklist": https://productschool.substack.com/p/product-management-resume-checklist
- The Interview Guys, career-changer summaries: https://blog.theinterviewguys.com/?p=2729
- Toptal, objective versus summary: https://www.toptal.com/resume/career-center/resume-objective-vs-resume-summary-key-differences-and-when-to-use-each
- Recruiter.com, "Is the Resume Objective Statement Truly Dead?": https://www.recruiter.com/i/is-the-resume-objective-statement-truly-dead/
Not used: the "340% more callbacks" claim (no method) and the 2018 and 2025 attention figures reported by one site (could not be verified elsewhere).

## 8. How LLM-assisted writing behaves, and how to separate the work (added 2026-10-10)

Status for this section: Reasoned from model behavior observed in this project. No external study was gathered. Treat each statement as a working assumption that the process is built to withstand, not as a finding.

### 8.1 Behaviors the process has to plan for

1. **Polish by default.** A model improves text it was not asked to improve. The finishing contract already forbids this for unflagged lines. The same pull applies to approved bullets, which must be stored exactly as the candidate approved them.
2. **Fluent and generic.** Without strong constraints, drafts converge on a plausible, interchangeable professional register. The candidate's own phrasing is the correction, not a lightly edited draft of the model's.
3. **Words before facts.** Offering polished options before the facts and positioning are settled invites rejection and wasted rounds. In the session that produced these rules, two rounds of polished summary options were rejected, and the candidate then said they were unhappy with how the options presented them. The fix is to elicit the candidate's own rough statement first and edit it.
4. **Pressure to fill gaps.** A sentence that needs a number or a scope tends to acquire one. The rule is to flag a missing measure, never supply it (section 2, X-Y-Z).
5. **Context carries over.** A long session accumulates rejected drafts, process chatter and earlier framings, and later output inherits them. This is the document-level form of the compounding problem the master resume exists to stop.
6. **One posture does not fit all tasks.** Interrogating evidence rewards doubt and precision. Building tools rewards determinism and tests. Writing prose rewards voice and economy. Doing them in one conversation degrades each: evidence work gets loose, prose gets cautious and choppy.
7. **Authorship is visible.** The candidate reads certain punctuation as an AI tell (house style), and some hiring-manager surveys report rejection of AI-generated application materials, though those figures are weak (tier 5, 19.6% in one survey versus an unclear 49% in another; see the evidence file). The shipped wording should be the candidate's own edited words.

### 8.2 Required separation: three kinds of session

Each kind runs in its own fresh session, started from a short written handoff that names the persona, the permitted inputs, the outputs and the forbidden actions. Do not carry one kind's conversation into another.

| Session | Persona | Does | Inputs | Output | Must not |
|---|---|---|---|---|---|
| A. Evidence (bullets) | Evidence interviewer: a skeptical editor who checks every claim against the record | Drafts candidate bullets from one role's WHD anchors, challenges numbers and verbs, asks one question at a time, stores the candidate's exact words | WHD anchors, voice sample, the bullet rules | Approved bullets in the library, each with its anchor and capability tags | Write summary prose; invent a measure; polish an approved line; change the WHD without a patch |
| B. Prose (summary variants) | Voice editor: writes in the candidate's register and edits the candidate's own rough lines | Starts by asking the candidate for rough statements in their own words, then tightens them within sections 7.1 and 7.2 | Approved bullets (read-only), voice sample, the target family, the candidate's rough lines | Two or three summary variants, each claim tagged with the supporting bullet ids | Introduce any claim that has no approved bullet; edit bullets; touch code or schemas |
| C. Process (code, schemas, lints, contracts) | Engineer: deterministic, tested, narrow | Changes helpers, schemas and contracts; runs the test suite | The repo, the TODO list | Committed code and tests | Draft resume wording; approve bullets; edit the WHD |

Session B runs after the library holds approved bullets for the roles it will draw on (rule S5 depends on it). Storage for summary variants and a check that every summary claim maps to a bullet id are not yet built; they are tracked as TODO #30.
