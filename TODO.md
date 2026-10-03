# TODO

Superseded items archived to `archive/TODO_v1.md` and `archive/TODO_v2.md`. This file tracks only what remains for v3.

## v2 public release
For strangers to install and use the skill without the author's data:
- [ ] Onboarding mode: port the Pre-Stage Career Documentarian interview into the skill (new users have no WHD)
- [x] ~~README rewrite: describe v2 install and use~~ — done 2026-09-16
- [x] ~~Strip any incidental personal references from `docs/`~~ — verified clean 2026-09-16 (v1 docs archived; no personal name/contact info found in `archive/` or `archive/prompts/`, only generic "LinkedIn" mentions as an input-source type)
- [ ] Phase 7 validation replay (v2 vs v1 on past JDs)

## v2 known defects (review 2026-09-24)
Twelve defects found in a code review and a live run. All are confirmed against
the code except #8, which is a process gap. Paths are relative to
`.claude/skills/resume-fit/`. Each group is ordered by priority, highest first.

### A. Fixable without input (mechanical fixes, default behavior is clear)

- [x] **1. The "blind" recruiter screen can see Work History information.**
  The screening step is supposed to judge the resume the way a recruiter would, with no access to the Work History Document (WHD). But `helpers/gapmap_summary.py` passes it a "seeker archetype" label that the fit step builds from the resume *and* the WHD. So the screen can be quietly optimistic, crediting experience the recruiter would never see. The canary check can't catch this, because it only looks for one literal token.
  *Fix:* have the fit step produce a resume-only archetype and pass only that to the screen.

- [x] **2. The ATS keyword check counts ordinary words as skill matches.**
  `helpers/ats.py` expands keywords through a synonym list, and some synonyms are common English words. Tested: "Go" matches "we go to market", "REST API" matches "the rest of the team", "Node.js" matches "each node in the graph", "AI" matches any "ai". Also, `pm` maps to project management, so a product manager's resume gets credit for project management. The result is an inflated ATS coverage score on every run, including the final re-check before a resume is finalized.
  *Fix:* match short or ambiguous synonyms only in their exact written form (case-aware), and split the product/project PM mapping.

- [x] **3. Edits made directly in the Word file are silently lost.**
  The pipeline treats `resume_candidate.md` as the source and renders the `.docx` from it (`helpers/render_docx.py`), one way only. When you edit the `.docx` by hand, the next pass works from the stale `.md` and overwrites or ignores your changes. This happened repeatedly in a live run.
  *Fix:* before any edit pass, compare the `.docx` and the `.md` (timestamp plus text). If they differ, stop and pull the `.docx` changes back into the `.md` first.

- [x] **4. Nothing enforces newest-first role ordering.**
  The contracts never say roles must appear in reverse chronological order. Only the WHD template mentions it. In a live run, an old role landed at the top of the resume.
  *Fix:* add the rule to the drafting contract, plus a helper that reads each role's dates in the draft and fails if they are out of order.

- [x] **5. A helper's output file gets corrupted on Windows.**
  `SKILL.md` has you save `gapmap_summary.py` output with a shell `>` redirect. On Windows that redirect can write in a non-UTF-8 encoding and garble special characters. This corrupted `gapmap.summary.yaml` in a live run.
  *Fix:* add an `--out <file>` option so the script writes the file itself as UTF-8, and update the instruction.

- [x] **6. The ATS character checker crashes on Windows.**
  `helpers/ats_chars.py` is the tool that finds unsafe characters, but it crashes as soon as it tries to print one (for example an arrow) to the Windows console. Every run has needed a manual `PYTHONIOENCODING=utf-8` workaround.
  *Fix:* have the script set its own output to UTF-8, and check the other helpers for the same problem.

- [x] **7. Edit instructions can name a vague location.**
  Each prescription says where a change goes (`target` in `schemas/prescriptions.schema.yaml`), but the field accepts any text. One prescription said "under the summary *or* as a new entry." The drafting step had to guess, guessed wrong, and that caused the ordering defect in #4.
  *Fix:* require one specific location per prescription and have validation reject "X or Y" targets.

- [x] **8. The length-trimming step can skip sections.** *(Process gap, not a code bug.)*
  When the resume runs long, the instructions say to weigh every section's space cost against its value before cutting. In a live run this was done only partly the first time.
  *Fix:* have `helpers/length_budget.py` print a section-by-section checklist that must be fully answered before the resume can be called "fits".

- [x] **9. The WHD leak detector is never set up.**
  The screen's last-resort leak check looks for a unique secret token (a "canary") that should exist only in the WHD. The template says one is generated automatically, but no code does it. A WHD made from the template keeps the placeholder token, so the check is weak.
  *Fix:* add a command that writes a random token into the WHD, and have `canary.py` refuse to run on the placeholder.

Group A done 2026-09-24: new helpers `chrono_check.py`, `docx_drift.py`,
`console.py`; `canary.py init`; `length_budget.py --review`;
`gapmap_summary.py --out` with resume-only `seeker_archetype_resume`; UTF-8
console output in every helper that prints document text. Tests: 97 passed / 3
skipped, now 133 passed / 0 skipped. Checked on real runs: `chrono_check.py`
flags the NASA Ames ordering defect in the Endless `resume_draft.md`,
`prescriptions.py` flags 7 hedged targets in the Endless run, and ATS coverage
is unchanged on the Anthropic and Endless resumes (no real terms lost).

- [x] **13. Three data-plane tests always skip.** `tests/test_ats_chars.py`, `tests/test_length_budget.py` and `tests/test_relevance.py` hardcode `D:/vibe/resume-pipeline-data/...`, but the data plane is now `D:\vibe\career-diagnostic-pipeline-data`. Resolve the path through `helpers/config.py` instead.

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

- [x] **14. The real WHD has no anchors.** Found while checking #11 against real data: `Reyes_WorkHistory_v4.md` contains zero `<!-- anchor: ... -->` markers (it predates the anchored template). Every `whd_patch.py` target, every `whd_anchors.py` citation, and every prescription `source` therefore fails to resolve on real data; the 4 proposed Endless patches already note "ANCHOR DOES NOT YET EXIST". Needs a one-time migration: add `role-N` / `role-N.project-M` / `beyond-employment` / `voice-sample` / `changelog` anchors and the front-matter `roles:` index, reviewed by the user. Blocks applying the pending WHD corrections (patent count, stale committee title, MOS figure, GoPro claim).
  **Progress 2026-09-24:** Stage 1 done. `helpers/whd_migrate.py` wrote `Reyes_WorkHistory_v5.md` (v4 untouched): 111 stable slug anchors (roles, role subsections, projects, voice sample, beyond-employment subsections, changelog), roles newest-first, 347 counter-numbered bullets and 24 `****` runs fixed, front-matter `roles:` index; `--check` proves the 684 content lines are identical. Template, fixture and examples switched to slug anchors. Stage 2 decisions approved 2026-09-24 (role structure, per-role `resume_default` include / context-only / omit; see the plan file): Team Kettering PAC nested under Doorstep Democracy; new roles Exploration Solutions (with Before You Submit), Burning Man, Precinct Captain (omit: political), Lockheed Martin (context-only); Zero Gravity Corp. context-only. Stage 2 implemented 2026-09-24 in the data-plane v5 (12 roles, 129 anchors; every removed line was a renamed or renumbered heading, verified) and the fit / synthesis / finishing contracts now honor `resume_default`. Tags approved and written 2026-09-30. Stage 2c (Precinct Captain nested under Doorstep Democracy; 11 roles) and Stage 3 (208 lines, punctuation only, words verified unchanged; Voice Sample untouched) applied 2026-09-30. Stage 4 done 2026-09-30: user reviewed and approved v5; v4 moved to `pipeline/whd/archive/`; 8 corrections (patent count to 2 in three places, committee title, advisor mention removed and redacted from the changelog, MOS gain, Artemis trans-lunar) and the 4 Endless evidence patches (retargeted to real anchors) applied and marked `applied`.- [ ] **15. Existing run gapmaps predate `seeker_archetype_resume`.** All 3 real `gapmap.yaml` files lack it, so `validate.py` and `gapmap_summary.py` now fail on them by design. Resuming the Endless run needs that one field added (resume-only archetype). Old `requirements.yaml` files lack location facts and simply yield a location open-question.
  **Note 2026-10-03:** expected to close through the master-resume design items (drop the per-run field and compare the screen's own read to a stable `candidate_type`) rather than by migrating the old gapmaps. Whatever replaces the field must keep the screen's read resume-only (see defect #1).

- [x] **10. Job location and remote/hybrid status are never captured.**
  The job-description parse (`schemas/requirements.schema.yaml`) has no field for location or work arrangement, and none for the source URL. A hybrid New York role was evaluated without ever considering that you are based in Ohio, so the "stop or proceed" gate (Gate 1) could not flag it.
  **Decided (grill-me 2026-09-24):**
  - *Rule storage:* new `pipeline/whd/preferences.yaml` in the data plane, next to the WHD but a separate file (preferences are not work history). Phase A reads it; each run folder records a copy so old verdicts stay explainable.
  - *Home base:* Kettering, OH. Commute radius from Kettering: **60 min one way for on-site (daily)**, **90 min for hybrid (3 days/week or fewer)**. So hybrid Columbus or Cincinnati passes as a commute.
  - *Relocation:* open to New York, Columbus, San Francisco Bay Area, Washington DC, **only with an employer-paid relocation package**. Each metro reaches **60 min from its core** (e.g. Columbia MD counts as DC; Jersey City and Stamford count as NY; San Jose and Oakland count as the Bay Area).
  - *Schema:* add `location`, `work_arrangement` (remote | hybrid | onsite | unstated), `hybrid_days` (if stated), `relocation_support` (offered | not-offered | unstated), and `source_url` to `requirements.yaml`.
  - *Gate 1 outcomes:*

    | JD location | Result |
    |---|---|
    | Remote | pass |
    | Hybrid/on-site within the commute radius | pass |
    | In a listed metro, relocation offered | pass |
    | In a listed metro, relocation unstated | no trip; required Open Question ("ask the recruiter about relocation support") |
    | Location unstated, or a borderline metro edge | no trip; required Open Question |
    | In a listed metro, relocation explicitly not offered | **trip** |
    | Anywhere else, hybrid/on-site | **trip** |

    A location trip fires on its own, independent of the skill-gap count, and uses the existing three options. "Contest" means "I'd make an exception for this role."

- [x] **11. The Work History can't be corrected, only added to.**
  `helpers/whd_patch.py` only appends text to the end of a section. Correcting a fact (3 patents to 2, a changed title) leaves the wrong version in place beside the right one, and later runs read both. Several real corrections from the last run are waiting on this. Separately, "hard no" markers (things you confirmed you can't claim) never expire, even after you gain the experience.
  **Decided (grill-me 2026-09-24):**
  - *Corrections replace in place.* A `correction` patch (the kind already exists in `schemas/patches.schema.yaml` but is applied as an append) carries `old` and `content`. `old` must match exactly once inside `target_anchor`, or the patch fails loudly. The WHD body holds only current facts; the changelog entry records the old text, the new text, and the run that prompted it (the data plane is not under git, so the changelog is the only history). Not strike-through: the fit subagent reads the body and cannot be trusted to ignore struck text.
  - *Hard-no markers never expire on their own.* When a JD touches a marker older than 12 months, the report adds an Open Question ("You marked this a hard no N months ago. Still true?"). "Still true" refreshes the date; "no" becomes an evidence patch that replaces the marker.
  - *Full hard-no review:* new helper `hard_nos.py <whd.md>` lists every marker with its age (deterministic). A skill review mode (e.g. `/resume-fit review-hard-nos`) calls it and walks each marker: still true / now have evidence / remove. The review date is stored as `hard_no_reviewed: YYYY-MM-DD` in the WHD front-matter.
  - *Reminder:* Phase A shows a one-line, non-blocking reminder when the last full review is more than 6 months old. The review also runs as part of a full WHD rebuild after a major life change.
  - No markers exist today, so there is nothing to migrate.

- [x] **12. "Partial" matches fall through the cracks.**
  Each requirement is rated Match, Partial or None. The rules for Partial disagree across files. `contracts/fit.md` defines a recoverable gap as None *or* Partial but then says to flag only None. `helpers/gate1.py` counts only None. Result: a hard requirement you only partly meet, with nothing better in the WHD, can never trigger the gate. A Partial that the WHD *could* strengthen can also skip the rule that every recoverable gap gets a fix.
  **Evidence (3 real runs):** the fit step already marks Partial rows recoverable when the WHD is stronger (it follows the definition, not the "None only" line). Gate 1 has never been able to trip: Endless had all 4 hard requirements short of a match and passed; Quidient's hr-7 (hard, Partial, not recoverable) was ignored.
  **Decided (grill-me 2026-09-24):**
  - *Definition:* recoverable = None or Partial on the resume AND the WHD holds stronger evidence. Fix the "only None" line in `contracts/fit.md`. `prescriptions.py` is unchanged (it already requires an Add for every recoverable row, Partials included).
  - *New gap review (Phase B.5, after fit, before Gate 1):* one batched round listing **every None** (recoverable or not, so each can be confirmed) and **every non-recoverable Partial**, hard requirements first. Recoverable Partials are skipped. Per row:
    1. "Real gap" → hard-no candidate (item 11 marker, confirmed in Phase H). For a recoverable None, "confirm" means the WHD evidence stands and the mandatory Add applies.
    2. "I have evidence I didn't record" → micro-interview → WHD patch proposal → re-classify the row.
    3. "Reframe something already in the WHD" → the user names the experience → re-classify against that WHD anchor.
    Any upgrade must cite a WHD anchor; synthesis's honesty check can still label it Stretch. Re-run `gate1.py` on the updated gapmap.
  - *Gate 1 tally:* a hard requirement that stays Partial and not recoverable counts as **0.5** of an unrecoverable gap (matches the 0.5 score weight). Trip rules unchanged (>= 2, or > 1/3 of hard requirements). The Gap Brief lists weak Partials separately from Nones.

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

- [x] **16. Contact details placed only in a header, footer, or text box go unnoticed.**
  Greenhouse documents this as a parse failure [S1]. `render_docx.py` cannot emit headers or footers, so the risk is in source resume files the user supplies.
  *Fix:* a check on input .docx files that fails when name, email, or phone appear only in a header, footer, or text box.
  **Done 2026-10-03:** `helpers/contact_check.py` (body, table, header, footer and text-box regions; `--name` optional). Its `docx_text_by_region()` is reusable for the extraction round trip (#26, #27).

- [ ] **17. Abbreviated titles and bare company names are not flagged.**
  Greenhouse: "Sr." style titles and company names without Inc., LLC, and similar parse poorly [S1]; job title is a weighted, recency-boosted match criterion [S33, S34].
  *Fix:* a helper that expands abbreviated titles ("Sr." to "Senior"), suggests a legal identifier where truthful, and flags divergence from the JD's title family.
  **Progress 2026-10-03:** detection done in `helpers/structure_lint.py` (abbreviated titles fail with the expansion named; a missing legal identifier is an advisory). Still open: suggesting a legal identifier (needs your confirmation of the true legal name) and the JD title-family divergence check.

- [x] **18. Section headings and date formats are not checked.**
  Missing or inconsistent sections cause partial parses [S1]; nonstandard headings were flagged in a direct test [S93].
  *Fix:* enforce a heading allowlist (Summary, Experience, Education, Skills) and one date format across entries.
  **Done 2026-10-03:** `helpers/structure_lint.py`. Decided: the core four are the default allowlist; other `##` headings are advisory and can be accepted with `--allow` (for example Patents).

- [x] **19. No file-size gate.**
  Google caps uploads at 2 MB [S3]; Greenhouse stops parsing above 2.5 MB [S1].
  *Fix:* fail any rendered output over 2 MB.
  **Done 2026-10-03:** `helpers/filesize_gate.py`.

- [ ] **20. `ats_chars.py` overstates its evidence.**
  The wording "documented ATS parsing failure points" appears in `helpers/ats_chars.py`, `contracts/finishing.md` and `tests/test_ats_chars.py`. No tier-1 or tier-2 source supports it for dashes, curly quotes or "&", and two direct tests extracted dashes and curly quotes intact [S93, L1].
  *Fix:* relabel dash, quote and arrow flags as house style (the no-dash rule can stay as a style rule); keep emoji and icon flags as hygiene; keep the "&" check only where the JD phrase is a plausible recruiter search term.
  **Progress 2026-10-03:** relabeled. Each violation now has a `category` (house-style, hygiene, search-term); docstring, reasons, `contracts/finishing.md` 6b and the test docstring no longer claim a documented parsing failure. `clean` and the exit code are unchanged. Still open: limiting the "&" flag to likely JD search terms (needs the JD).

- [ ] **21. The screening gates cite unreliable timings, and the simulation's own bias is unstated.**
  "6-second" and "3-minute" appear in `contracts/screening.md`, `schemas/screen.schema.yaml` (comments) and `templates/appendix.md`. The timings come from thin vendor studies [S74, S75]; the attention pattern (title, employer, dates first) is the durable finding. The simulation is LLM-run, and published studies show LLM verdicts shift with framing, authority and gender cues [S95, S96].
  *Fix:* rename the gates "fast scan" and "deep read"; have Gate 1 check current title, employer, dates and location in the top third of page one; add a limitations note on LLM-evaluator bias and keep the approximation framing.
  **Progress 2026-10-03:** gates renamed in the contract, schema comments, appendix template and the committed example outputs (schema keys such as `gate1_verdict` unchanged); limitations note added as `contracts/screening.md` section 6. Still open: the top-third-of-page-one check.

- [ ] **22. Bullets without a measure or method pass unflagged.**
  Google asks for data and recommends "accomplished X as measured by Y, by doing Z" [S78, S80].
  *Fix:* an advisory check that flags bullets lacking a measure (Y) or a method (Z). Absorbs Antigravity item A3.

- [ ] **23. `length_budget.py` treats page three like any overflow.**
  No ATS page penalty was found; two pages are preferred for experienced roles [S71, S78].
  *Fix:* keep the two-page default; at three pages require a stated reason tied to unique evidence; check that the strongest metric sits in the top third of page one.
  **Progress 2026-10-03:** `length_budget.py --reason TEXT` records an override; the result flags a real third page (above 2.5 estimated pages) and the CLI says the reason must name unique, relevant evidence. Still open: the top-third strongest-metric check.

### D. Needs your decision first

- [ ] **24. Knockouts beyond location are not captured.**
  Auto-rejection runs on recruiter-configured application questions [S15, S16, S21, S22, S23]. Location and relocation are handled (#10); work authorization, years of experience and salary are not.
  *Decide:* which of these to store in `pipeline/whd/preferences.yaml` (a salary floor is sensitive), and whether Gate 1 or a pre-apply checklist compares them with the JD and the resume.

- [ ] **25. The ATS coverage percentage reads as a score.**
  Per-requirement verdicts already exist in the gapmap (#12), which matches how Workday Fit & Gap and Ashby evaluate [S28, S29, S30]. `ats.py` adds a literal-term coverage percentage that no vendor uses as a threshold, and synonym hits do not stack in Greenhouse scoring [S12]. Scoring favors skills shown in recent, dated roles [S33, S39].
  *Decide:* demote `ats.py` output to "recruiter-search term gaps" split by required and preferred terms, and add an `evidence_location` field to gapmap rows (recent dated role / older role / skills list only).

- [ ] **26. PDF output.**
  Text PDFs and .docx are both accepted [S1, S3]. In a local test, LibreOffice headless export produced a tagged PDF, but python-docx's default bullet extracted as private-use U+F0B7 [L1].
  *Decide:* whether to add PDF output; if so, export (not print) with LibreOffice headless, replace the Symbol-font bullet, and add a local extraction round trip (`pdftotext`) that fails on private-use characters, scrambled reading order, or contact details found only in a header.

- [ ] **27. No step checks the resume in a real parser.**
  Employer autofill previews and vendor trials are real parsers [S3, S6, S42]; Textkernel and Affinda need accounts and are proprietary.
  *Decide:* add a manual finishing step (autofill preview first, vendor trial optional) that records mismatched fields in the run folder, and whether it is required or optional.

- [ ] **28. Headings are built from manual bold and size.**
  Using Word heading styles is a hypothesis from an unsourced briefing [U1]; no parser vendor documents relying on them.
  *Decide:* whether to switch `render_docx.py` to restyled "Heading 1" / "Heading 2".

- [ ] **29. Contact links may hide the URL.**
  Link text such as "LinkedIn" leaves the address out of extracted text (reasoned; see the guidance file).
  *Decide:* whether to make "show full URLs as visible text" a house rule.

### Reviewed and closed: Gemini Antigravity proposals (2026-10-03)
These three items were appended by the Gemini Antigravity run (commit 3f9f0f7).
Dispositions follow the evidence review in `docs/research/ats-evidence-2026.md`.

- [x] ~~**A1. Upgrade helpers/ats.py to support semantic matching.**~~ Closed as duplicate: the model already adjudicates semantic terminology mismatches (`ats.py` docstring), and the fit step judges each requirement. The evidence-backed change is #25.
- [x] ~~**A2. Add 'Generic AI language' flag to contracts/screening.md.**~~ Closed as unsupported: its cited source could not be found, and no evidence shows recruiters reject specific words such as "spearheaded".
- [x] ~~**A3. Implement the Google 'XYZ Formula' check.**~~ Merged into #22.

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
