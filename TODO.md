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

- [ ] **10. Job location and remote/hybrid status are never captured.**
  The job-description parse (`schemas/requirements.schema.yaml`) has no field for location or work arrangement, and none for the source URL. A hybrid New York role was evaluated without ever considering that you are based in Ohio, so the "stop or proceed" gate (Gate 1) could not flag it.
  *Your input:* your rules for location. Remote only? Hybrid within a set commute? Open to relocating, and where? Is a mismatch a hard stop or a warning?

- [ ] **11. The Work History can't be corrected, only added to.**
  `helpers/whd_patch.py` only appends text to the end of a section. Correcting a fact (3 patents to 2, a changed title) leaves the wrong version in place beside the right one, and later runs read both. Several real corrections from the last run are waiting on this. Separately, "hard no" markers (things you confirmed you can't claim) never expire, even after you gain the experience.
  *Your input:* should a correction overwrite the old text, or keep it struck through with a date? Should "hard no" markers be revisited after a set time?

- [ ] **12. "Partial" matches fall through the cracks.**
  Each requirement is rated Match, Partial or None. The rules for Partial disagree across files. `contracts/fit.md` defines a recoverable gap as None *or* Partial but then says to flag only None. `helpers/gate1.py` counts only None. Result: a hard requirement you only partly meet, with nothing better in the WHD, can never trigger the gate. A Partial that the WHD *could* strengthen can also skip the rule that every recoverable gap gets a fix.
  *Your input:* should a weak Partial on a hard requirement count toward stopping the application? Should every Partial with WHD support get a mandatory fix?

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
