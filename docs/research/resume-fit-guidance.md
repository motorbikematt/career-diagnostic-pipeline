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
