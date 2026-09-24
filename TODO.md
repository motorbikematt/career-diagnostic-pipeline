# TODO

Superseded v1 items archived to `archive/TODO_v1.md`. This file tracks only
what remains for v2.

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
