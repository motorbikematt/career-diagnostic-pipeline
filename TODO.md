# TODO

Superseded items archived to `archive/TODO_v1.md` and `archive/TODO_v2.md`. This file tracks only what remains for v3.

## v2 public release
For strangers to install and use the skill without the author's data:
- [ ] Onboarding mode: port the Pre-Stage Career Documentarian interview into the skill (new users have no WHD)
- [ ] Phase 7 validation replay (v2 vs v1 on past JDs)

## v2 known defects (review 2026-09-24)
Twelve defects found in a code review and a live run. All are confirmed against
the code except #8, which is a process gap. Paths are relative to
`.claude/skills/resume-fit/`. Each group is ordered by priority, highest first.

### A. Fixable without input (mechanical fixes, default behavior is clear)

Group A done 2026-09-24: new helpers `chrono_check.py`, `docx_drift.py`,
`console.py`; `canary.py init`; `length_budget.py --review`;
`gapmap_summary.py --out` with resume-only `seeker_archetype_resume`; UTF-8
console output in every helper that prints document text. Tests: 97 passed / 3
skipped, now 133 passed / 0 skipped. Checked on real runs: `chrono_check.py`
flags the NASA Ames ordering defect in the Endless `resume_draft.md`,
`prescriptions.py` flags 7 hedged targets in the Endless run, and ATS coverage
is unchanged on the Anthropic and Endless resumes (no real terms lost).

### B. Needs your decision first (design or preference choices)

Group B done 2026-09-24: new helpers `location_gate.py`, `hard_nos.py`,
`gap_review.py`, `whd_io.py` (CRLF-preserving WHD writes, shared front-matter
setter); `whd_patch.py` corrections replace in place; `gate1.py` weighted tally,
location check and `--out`; schemas `location` and `preferences`; template
`preferences-template.yaml`; SKILL.md Phase A location + hard-no reminder,
Phase B.5 gap review, hard-no review mode. Real preferences written to
`pipeline/whd/preferences.yaml`. Tests: 172 passed. Checked on real runs:
Endless (hybrid NY) and Quidient (hybrid Columbia MD) both give a location
open-question; Quidient hr-7 is a weak Partial (tally 0.5); no run trips Gate 1,
but the gap review now surfaces 4 rows (Endless) and 3 (Quidient).
Follow-ups in the same pass: `whd_patch.py apply_file` marks written patches
`status: applied` (Phase B.5 / Gate 1 apply immediately and Phase H re-applies
the queue, so without this a patch landed twice); `gate1.py` rejects a gap-review
upgrade that skipped `whd_evidence` / `recoverable` / `review.anchor`.

## ATS evidence alignment (research 2026-10-03)
Rules and the rule audit live in `docs/research/resume-fit-guidance.md`; the
evidence and the bracketed source IDs ([S#], [L#], [U1]) live in
`docs/research/ats-evidence-2026.md`. Paths are relative to
`.claude/skills/resume-fit/`. Each group is ordered by priority, highest first.
Already covered by done items: case-aware keyword matching (#2), location and
relocation knockouts (#10), and per-requirement Match / Partial / None verdicts
with the hard vs preferred split and Gate 1 (#12).

### C. Fixable without input

Standalone-helper pass done 2026-10-03: new `filesize_gate.py`, `contact_check.py`,
`structure_lint.py`, `env_check.py`; `ats_chars.py` categories; `length_budget.py
--reason`; screening gate rename. The new lints are listed in the SKILL.md helper
table but NOT yet wired into `contracts/finishing.md` 6b (decided: wire them with
the master-resume work). Tests: 189 passed, now 220.

- [ ] **17. Abbreviated titles and bare company names are not flagged.**
  Greenhouse: "Sr." style titles and company names without Inc., LLC, and similar parse poorly [S1]; job title is a weighted, recency-boosted match criterion [S33, S34].
  *Fix:* a helper that expands abbreviated titles ("Sr." to "Senior"), suggests a legal identifier where truthful, and flags divergence from the JD's title family.
  **Progress 2026-10-03:** detection done in `helpers/structure_lint.py` (abbreviated titles fail with the expansion named; a missing legal identifier is an advisory). Still open: suggesting a legal identifier (needs your confirmation of the true legal name) and the JD title-family divergence check.

- [ ] **20. `ats_chars.py` overstates its evidence.**
  The wording "documented ATS parsing failure points" appears in `helpers/ats_chars.py`, `contracts/finishing.md` and `tests/test_ats_chars.py`. No tier-1 or tier-2 source supports it for dashes, curly quotes or "&", and two direct tests extracted dashes and curly quotes intact [S93, L1].
  *Fix:* relabel dash, quote and arrow flags as house style (the no-dash rule can stay as a style rule); keep emoji and icon flags as hygiene; keep the "&" check only where the JD phrase is a plausible recruiter search term.
  **Progress 2026-10-03:** relabeled. Each violation now has a `category` (house-style, hygiene, search-term); docstring, reasons, `contracts/finishing.md` 6b and the test docstring no longer claim a documented parsing failure. `clean` and the exit code are unchanged. Still open: limiting the "&" flag to likely JD search terms (needs the JD).

- [ ] **21. The screening gates cite unreliable timings, and the simulation's own bias is unstated.**
  "6-second" and "3-minute" appear in `contracts/screening.md`, `schemas/screen.schema.yaml` (comments) and `templates/appendix.md`. The timings come from thin vendor studies [S74, S75]; the attention pattern (title, employer, dates first) is the durable finding. The simulation is LLM-run, and published studies show LLM verdicts shift with framing, authority and gender cues [S95, S96].
  *Fix:* rename the gates "fast scan" and "deep read"; have Gate 1 check current title, employer, dates and location in the top third of page one; add a limitations note on LLM-evaluator bias and keep the approximation framing.
  **Progress 2026-10-03:** gates renamed in the contract, schema comments, appendix template and the committed example outputs (schema keys such as `gate1_verdict` unchanged); limitations note added as `contracts/screening.md` section 6. Still open: the top-third-of-page-one check.

- [x] **22. Bullets without a measure or method pass unflagged.**
  Google asks for data and recommends "accomplished X as measured by Y, by doing Z" [S78, S80].
  *Fix:* an advisory check that flags bullets lacking a measure (Y) or a method (Z). Absorbs Antigravity item A3.
  **Done 2026-10-30 for the measure half:** `helpers/bullet_lint.py` (advisory, always exits 0) flags `duty-opener` ("responsible for", "worked on", "helped with" and the like, after any bold label), `no-measure` (no number and no stated result: an activity-only bullet) and `vague-qualifier` ("significantly" with no number), and counts bullets that state a result only in words as information. Each flag carries the role's recency rank; the two newest roles are `priority`. `--review <work>/measure_review.yaml` records the candidate's answers (`no-measure` or `keep`, keyed by the bullet's first 60 normalized characters) so a later round does not ask again; stale keys are reported. A thin Measure round in `contracts/finishing.md` asks about priority flags (batches of about three, the candidate's own words inserted, never a supplied figure); the lint also runs on the seed resume in Phase E and as re-eval axis 8. On the seven past runs: 114 bullets, 71 with a number, 11 with a result in words, 32 activity-only (15 in the two newest roles), 0 duty openers, 0 vague qualifiers.
  **The method half (Z) is not linted, by decision:** only 26 of 114 bullets use "by", "via", "using" or "through", and good bullets put the method in the action verb, so a word rule would flag about three bullets in four. Asking for the method moves to the evidence interview (TODO 42). Limits: a digit is a weak proxy for a measure ("Led 3 meetings" passes), and the outcome-wording list is loose on purpose. Not built: a check that the WHD holds a number the bullet did not use (needs the bullet library to map bullets to anchors) and "from X to Y" baseline detection.

- [ ] **23. `length_budget.py` treats page three like any overflow.**
  No ATS page penalty was found; two pages are preferred for experienced roles [S71, S78].
  *Fix:* keep the two-page default; at three pages require a stated reason tied to unique evidence; check that the strongest metric sits in the top third of page one.
  **Progress 2026-10-03:** `length_budget.py --reason TEXT` records an override; the result flags a real third page (above 2.5 estimated pages) and the CLI says the reason must name unique, relevant evidence. Still open: the top-third strongest-metric check.
  **Progress 2026-10-29:** the screen's escalation line (the metric that earns a call) is now located on the estimated page and flagged when it starts below the top two-thirds of page one (`density_lint.py --screen`, TODO 42). That is the screen's choice of strongest metric, not a separate judgment. It checks the two-thirds scan zone rather than the top third this item names; decide whether the top third still matters before closing.

### D. Needs your decision first

- [ ] **24. Knockouts beyond location are not captured.**
  Auto-rejection runs on recruiter-configured application questions [S15, S16, S21, S22, S23]. Location and relocation are handled (#10); work authorization, years of experience and salary are not.
  *Decide:* which of these to store in `pipeline/whd/preferences.yaml` (a salary floor is sensitive), and whether Gate 1 or a pre-apply checklist compares them with the JD and the resume.

- [ ] **25. The ATS coverage percentage reads as a score.**
  Per-requirement verdicts already exist in the gapmap (#12), which matches how Workday Fit & Gap and Ashby evaluate [S28, S29, S30]. `ats.py` adds a literal-term coverage percentage that no vendor uses as a threshold, and synonym hits do not stack in Greenhouse scoring [S12]. Scoring favors skills shown in recent, dated roles [S33, S39].
  *Decide:* demote `ats.py` output to "recruiter-search term gaps" split by required and preferred terms, and add an `evidence_location` field to gapmap rows (recent dated role / older role / skills list only).

- [ ] **26. PDF output.**
  Text PDFs and .docx are both accepted [S1, S3]. In a local test, LibreOffice headless export produced a tagged PDF, but python-docx's default bullet extracted as private-use U+F0B7 [L1].
  2026-10-09, Word export (`word_pages.py --pdf`, ExportAsFixedFormat): the same bullet extracted as a plain U+2022, so the private-use glyph is a LibreOffice artifact. New hazard found in the same test: a hyphenated word that wraps at a line end extracts damaged ("diffusion-based" to "diffusionbased", "zero-" + "downtime"); which words are hit moves with margins and font size. The .docx text is unaffected.
  *Decide:* whether to add PDF output; if so, export (not print) through Word where present (LibreOffice headless as the fallback, replacing its Symbol-font bullet), and add a local extraction round trip (`pdftotext -enc UTF-8`) that fails on private-use characters, scrambled reading order, hyphenated words split across lines, or contact details found only in a header.

- [ ] **27. No step checks the resume in a real parser.**
  Employer autofill previews and vendor trials are real parsers [S3, S6, S42]; Textkernel and Affinda need accounts and are proprietary.
  *Decide:* add a manual finishing step (autofill preview first, vendor trial optional) that records mismatched fields in the run folder, and whether it is required or optional.

- [ ] **28. Headings are built from manual bold and size.**
  Using Word heading styles is a hypothesis from an unsourced briefing [U1]; no parser vendor documents relying on them.
  *Decide:* whether to switch `render_docx.py` to restyled "Heading 1" / "Heading 2".

- [ ] **29. Contact links may hide the URL.**
  Link text such as "LinkedIn" leaves the address out of extracted text (reasoned; see the guidance file).
  *Decide:* whether to make "show full URLs as visible text" a house rule.

- [ ] **30. Summary rules are not enforced or stored.**
  `docs/research/resume-fit-guidance.md` sections 7 and 8 set rules for summaries (every claim traces to an approved bullet; two to four lines; no first person; no objective statement; a variant per target family). Nothing checks them, and there is no file for the variants.
  *Decide:* where summary variants live (a `summaries.yaml` next to `bullet_library.yaml`, each claim tagged with bullet ids), and whether to add an advisory lint for the mechanical rules (length, pronouns, objective phrasing) and a claim-to-bullet check. Do this after the bullet library exists.

- [ ] **31. The resume's location is not checked against the target market.**
  On Eightfold's Netflix career site the parsed location set the job pool: the header city if present, otherwise the most recent role's city; a relocation phrase had no visible effect [L2]. Location and relocation knockouts (#10) compare preferences with the JD, but nothing checks which city the resume itself presents.
  *Fix:* an advisory lint that reports the header location and the first location in the work history, and warns when the JD is on-site or hybrid in a different metro, or when the header has no location and the first role's city would be picked up instead.
  *Decide:* the wording to recommend for a candidate open to relocation (for example "Kettering, OH; relocating to {metro}" only when that is true), and whether the lint reads target metros from `pipeline/whd/preferences.yaml`.

## LinkedIn and recruiter guidance alignment (2026-10-22)
Rules, source labels and the full gap analysis live in `docs/research/linkedin-guidance-2026.md`
([W1], [W2] there). Paths are relative to `.claude/skills/resume-fit/`. Nothing here is
implemented. Items 32 and 33 wait on decisions D1 and D2 in that file; 41 waits on D3.
Related open items sharpened by this guidance: #17 (JD title-family divergence), #21 and
#23 (top-of-page-one checks), #22 (X-Y-Z check), #24 (knockouts), #25 (coverage percentage),
#30 (summary variants).

- [ ] **33. Title and scope policy.** (decision D2)
  The recruiter advises titling the resume with the target's title and giving the true title at the background check [W2]. The honesty check would class that as a Stretch. A truthful parenthetical carrying the scope is the safer form.
  *Decide:* default parenthetical, ratified swap with a background-check reminder, or never swap. Then add a Title-alignment prescription type, a `title_on_record` field and `scope_equivalent_titles` in the WHD role index, and a report line.

- [ ] **34. Requirements carry no emphasis.**
  The top third to two-thirds of a JD's requirements carry the core ask [W2]. `schemas/requirements.schema.yaml` stores hard versus preferred only.
  *Fix:* an `emphasis` field (core | supporting) set at intake from position in the JD; use it to order the Gap Map and report rows.

- [ ] **35. Synonym hits hide vocabulary gaps.**
  Recruiters and scoring look for the JD's wording [W2]; `ats.py` counts taxonomy synonyms as matches. Merges with #25.
  *Fix:* report synonym-only matches as a "vocabulary gap" and prescribe mirroring the JD term once, only where true.

- [ ] **36. Hidden-text lint for input resumes.**
  The guest says white or one-point text and prompt injection do not work [W2]; nothing checks supplied .docx files for them.
  *Fix:* a standalone helper that fails on white-on-white, font size at or below 2 pt, or hidden (vanish) runs. Fixable without input.

- [ ] **37. Age-signal advisory.**
  After about five years of experience, drop education years and GPA [W2]. `resume_default` covers old roles only.
  *Fix:* an advisory lint for graduation years and GPA on a resume whose experience exceeds five years, and a WHD flag marking them omit-by-default. Do not alter a required application field.

- [ ] **38. Scope line, top two-thirds, and unquantified filler.**
  Extends #21, #22 and #23: each recent role starts with a scope line; the scan zone is the top two-thirds of page one, not the top third; flag subjective adjectives in the summary as an advisory only (TODO A2 stays closed: no evidence of word rejection).
  **Progress 2026-10-23:** the scan zone is measured as the top two-thirds of page one, with a word ceiling, in `density_lint.py` (#42). Still open: the scope-line check and the summary adjective advisory.

- [ ] **39. WHD template lacks structured scope and education flags.**
  Add a "Scope facts" block per role (team, sites, budget, revenue, users), title-of-record fields (with #33), and an education-dates flag (with #37). Update `templates/whd-template.md`, `whd_anchors.py` and the migration helper, with tests.

- [ ] **40. No target families in preferences.**
  Official guidance: narrow to one or two targets by interest, skill and demand [W2]; one resume per target title [W1].
  *Decide:* a `target_families` list in `pipeline/whd/preferences.yaml`, used by #30 (summary variants) and by a Gate 1 warning when a JD falls outside every declared family.

- [ ] **41. No LinkedIn profile mode.** (decision D3)
  First-party guidance now exists for headline, About, Featured and Open to Work [W1, W2].
  *Decide:* a profile mode inside `resume-fit` that drafts headline options and a first-person About from the WHD (every claim traced to a WHD anchor, voice sample as the register, house style respected), flags resume and profile inconsistencies in title, dates and numbers, and suggests Featured items from Beyond Employment.

## Density and simplification (2026-10-23)

Source: the CAFE worksheet and Get Selected bullet grader review, and the 2026-10-22 LinkedIn makeover [W2]; see `docs/research/resume-fit-guidance.md` section 9. Six past candidate resumes measured 998 to 1,254 words, with a median bullet of about 35 words and 24 of 101 bullets carrying three or more numbers. The pipeline adds content and had no mechanism that subtracts it.

- [ ] **42. Resumes are dense and nothing measures scan cost.**
  **Done 2026-10-23 (build 1):** `helpers/density_lint.py` (advisory, always exits 0) with tests; run in Phase E on the seed resume, in the Phase G length round and in the 6b re-eval. Thresholds are owner-set and calibrated on six past runs, expected to be retuned: bullets 40 words, 2 numbers per bullet, role budget 5/4/2, role intro 40 words, scan zone 300 words, total 1,000 words. The length round is now content first, layout last: margin and font levers come only after the density lint is clean and the overflow is within about 0.1 page.
  **Done 2026-10-29 (build 2):**
  - *Escalation quote.* `screen.schema.yaml` gains an optional `escalation_quote`; `contracts/screening.md` 4b requires it for new runs (the exact resume words the trigger rests on, no figure the resume lacks). `canary.py --resume <resume.md>` fails a run whose quote is missing or not on the resume word for word, and warns when the trigger cites a figure the resume lacks. `density_lint.py --screen` locates the quote on the estimated page and flags `escalation-below-scan-zone` or `escalation-missing`, falling back to the quote's figures when a draft reworded the line. Matching is in `verbatim.py` (markdown, whitespace and curly quotes ignored; case, punctuation and dashes must match). Found while building it: the committed example run's `screen.yaml` and `report.md` cited "50k units", a figure only the example WHD holds, so the fixture was itself a blindness leak; fixed.
  - *Add paired with Cut.* `prescriptions.py --resume <resume.md>` projects bullets per Experience role (resume bullets, plus adds, minus cuts and removes; a compress does not offset) against the density lint's recency budget (5, 4, then 2) and fails an Add that grows a role past it, unless a cut or remove offsets it in the same role or the Add carries an approved `over_budget_reason`. New optional fields `role`, `bullets`, `over_budget_reason` in `prescriptions.schema.yaml`. Unknown roles and an Add that names a company with no `role` are notes, not failures. A role already over budget is not flagged unless an Add makes it grow.
  - *Not built:* a word budget (prescriptions never draft wording, so only bullet counts are checked here; the lint's word ceilings still apply to the draft). Runs made before 2026-10-29 have no `escalation_quote`, so `canary.py --resume` fails on them by design.
  *Still open:*
  - Evidence interviews (Phase B.5 new-evidence, Phase G Supply, Phase H) ask one open question. Use a structured cause, action, result-with-baseline, impact sequence, and record where each measure came from (exact, candidate estimate, unknown); never let the model supply a figure.
  - The 38% of past bullets with no number is #22 (done 2026-10-30), not density. The method question ("what steps and tools") has no lint and lives in this interview.

### Reviewed and closed: Gemini Antigravity proposals (2026-10-03)
These three items were appended by the Gemini Antigravity run (commit 3f9f0f7).
Dispositions follow the evidence review in `docs/research/ats-evidence-2026.md`.

## Post v1.0 (roadmap)
- [ ] Performance review support as Day 1 value proposition
- [ ] Interview preparation module (diary data already structured for this)
- [ ] Outcome tracking
- [ ] Cover letter generation (trivial Phase G extension)
- [ ] Chrome extension / job capture mechanism
- [ ] Application tracking / CRM
- [ ] GitHub Pages if non-technical users struggle with README
- [ ] Validate behavioral hypothesis (Workday Career Profile interviews)
- [ ] CareerLog hands-on evaluation
- [ ] LinkedIn profile consistency and referral prompts (advisory; no evidence gathered yet)
