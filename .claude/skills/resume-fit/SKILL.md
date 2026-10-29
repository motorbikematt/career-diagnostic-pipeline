---
name: resume-fit
description: >-
  Diagnose how well your resume fits a specific job description and get a concise
  verdict report (Apply / Apply with edits / Do not pursue) with a prescriptions
  table, honesty check, and shadow requirements — then, on request, a
  submission-ready resume. Invoke as /resume-fit with a JD file path, pasted JD
  text, or a JD URL. Use whenever the user wants to evaluate, tailor, or decide
  on applying to a specific job.
---

# resume-fit

Given a job description, produce one concise report and, when warranted, a
submission-ready `.docx`, improving the user's Work History Document (WHD) as a
side effect of each run.

**Three properties are load-bearing and must never be compromised:**
1. **Honesty guardrails** — stretch/hard-no classification; no fabrication.
2. **Screening blindness** — the screening step sees only what a recruiter sees,
   never the WHD (enforced by construction, not by instruction — see below).
3. **Conservative default** — when employer evidence is thin, do not assume.

## Two-plane model

- **Code plane** (this repo): skill logic, helpers, schemas, templates,
  synthetic examples. User-agnostic. No personal data, ever.
- **Data plane** (private, configured per user): the WHD, per-run folders, and
  fixtures. Located via configuration, never a hardcoded path.

## First-run setup (data-plane config)

`helpers/config.py` resolves the data plane from `$RESUME_FIT_DATA_PLANE`, then
`$XDG_CONFIG_HOME/resume-fit/config.yaml` (or `~/.config/resume-fit/config.yaml`).
If neither is set, ask the user where their private data folder lives and persist it:
```bash
python .claude/skills/resume-fit/helpers/config.py set "/path/to/data-plane"
```
The data plane must contain exactly one `pipeline/whd/<the WHD>.md`. A legacy WHD
without anchors must be migrated once (`whd_migrate.py <old> <new>`, then
`--check <old> <new>`; it never overwrites). The WHD needs a unique canary token
for the screening leak check (`canary.py init <WHD>`; safe to re-run).

## Run folder and output discipline

`runfolder.py` creates `<data-plane>/pipeline/runs/<company>-<role>-<date>/`
(`<run>`) with a `work/` subfolder (`<work>`). Below, every pipeline file is in
`<work>`. The top of `<run>` holds only what the user opens:

- `report.md` and `appendix.md` (Phase E), and
- after sign-off, the final `<LASTNAME>_<FIRSTNAME>_<COMPANY>_<DATE>.docx` (Phase G).

The final `.docx` is the only resume deliverable. `resume_candidate.md` is the
working source the docx is rendered from, never a deliverable. **Never write a
PDF.** Helper results go to stdout: do not redirect lint or measurement output
into the run, and do not save scratch copies, snapshots or variants of the
resume there (use a temp folder). `whd_patch.py` backs up the WHD itself, into
`pipeline/whd/backups/`; never copy the WHD into a run.

## Architecture

```
Phase A  INTAKE (orchestrator)         -> requirements.yaml, run folder
Phase B  PARALLEL research + fit        -> scd.yaml, gapmap.yaml
Phase C  GATE 1 Gap Brief (3 options)   -> Python tally + trip rules
Phase D  SCREENING (WHD-blind)          -> screen.yaml
Phase E  SYNTHESIS                       -> report.md + appendix.md
Phase F  GATE 2 user decision
Phase G  FINISHING LOOP                  -> the final .docx
Phase H  WHD RECONCILIATION              -> WHD patched
```

### Model routing (orchestrator parameter, not a per-stage ritual)
- **Cheap/fast model** (e.g. Haiku-class): research + fit extraction (Phase B).
- **Strong model** (Opus-class): screening simulation (Phase D) + synthesis (Phase E).

### Exception-driven interrogation (cross-cutting)
When any phase surfaces a *fundamental* mismatch (archetype incompatibility, a
load-bearing stretch, disqualifying research), pause and ask one question round
rather than carrying ambiguity into a more expensive phase. Cap: ~3 rounds per
gate; overflow to a punch list. Routine gaps wait for their designated phase.

---

## Phase A — Intake

1. **Validate inputs.** Confirm: a JD is present (file, pasted text, or URL);
   the current resume is located; the WHD is located in the data plane. If the
   data plane is unconfigured, run first-run setup above.
2. **Parse the JD once** into `requirements.yaml` (canonical schema —
   `schemas/requirements.schema.yaml`). Every downstream step consumes this
   schema, never the raw JD. Extract: company, role, seniority, hard vs.
   preferred requirements (each with an id and keywords), ATS keywords, and
   recruiter-persona cues. Also extract the **location facts exactly as the JD
   states them**: `location`, `work_arrangement` (remote | hybrid | onsite |
   unstated), `hybrid_days` if stated, `relocation_support` (offered |
   not-offered | unstated), and `source_url` when the JD came from a URL. No
   candidate-side judgment goes in `requirements.yaml`: the screening subagent
   receives it.
3. **Create the run folder:**
   ```bash
   python .claude/skills/resume-fit/helpers/runfolder.py "<Company>" "<Role>"
   ```
   Write `requirements.yaml` into `<work>`. The helper also snapshots
   `<data-plane>/pipeline/whd/preferences.yaml` (the candidate's deal-breaker
   rules; template: `templates/preferences-template.yaml`) into
   `<work>/preferences.snapshot.yaml`.
4. **Location assessment** (skip for a remote role): judge the geography and
   write `<work>/location.yaml` (`schemas/location.schema.yaml`):
   `drive_minutes_from_home` (from the preferences `home`), `nearest_metro` (an
   exact name from the preferences `relocation.metros`, or null),
   `metro_minutes` (drive from that metro's core), `borderline` (true for a
   genuine edge case), and a one-line `notes`. Estimate drive times from
   general knowledge; no maps API. Thresholds are NOT applied here: Gate 1
   applies them from the preferences file.
5. **Validate before proceeding** (structural drift fails loudly here):
   ```bash
   python .claude/skills/resume-fit/helpers/validate.py <work>/requirements.yaml requirements
   python .claude/skills/resume-fit/helpers/validate.py <work>/location.yaml location   # non-remote roles only
   ```
6. **Hard-no reminder** (one line, never blocks):
   ```bash
   python .claude/skills/resume-fit/helpers/hard_nos.py <data-plane>/pipeline/whd/<WHD>.md
   ```
   If `review_due` is true, say once: "Your hard-no list was last reviewed
   <last_review or never> (<marker_count> markers). Run the hard-no review now
   or skip?" See **Hard-no review mode** below. Keep the `stale` list for
   synthesis.

## Phase B — Parallel research + fit

Dispatch two subagents concurrently on the **cheap/fast model**. Each receives a
minimal manifest — the fit subagent never sees the SCD; the research subagent
never sees the resume or WHD.

- **Research subagent** — contract: `contracts/research.md`. Manifest:
  `requirements.yaml` (company/role) + web search. Writes `<work>/scd.yaml`.
- **Fit subagent** — contract: `contracts/fit.md`. Manifest: `requirements.yaml`
  + the resume + the WHD. Writes `<work>/gapmap.yaml`.

Validate both on return (fail loudly, not silently downstream):
```bash
python .claude/skills/resume-fit/helpers/validate.py <work>/scd.yaml scd
python .claude/skills/resume-fit/helpers/validate.py <work>/gapmap.yaml gapmap
```

**Exception-driven interrogation (fire only on FUNDAMENTAL mismatches):**
- *Fit:* Seeker vs. JD archetype structurally incompatible → ask whether
  repositioning is intended before screening simulates the wrong candidate.
- *Research:* SCD contradicts the resume's positioning, or surfaces something
  that changes whether the user wants the job (layoffs, acquisition, leadership
  exodus) → surface now, not in the report.

One question round each; overflow to a punch list. Routine gaps wait for their phase.

## Phase B.5: Gap review (before Gate 1)

The WHD only knows what the user remembered to write down; a requirement can
jog a memory, or show that something already in the WHD answers it once
reframed. List the rows to review:
```bash
python .claude/skills/resume-fit/helpers/gap_review.py <work>/gapmap.yaml <work>/requirements.yaml
```
It returns EVERY None (recoverable or not) and every non-recoverable Partial,
hard requirements first. Ask in batched AskUserQuestion rounds (hard first),
one of four answers per row, and record it on the row as
`review: {decision, anchor, note}`:

- **real-gap**: the gap is real. Queue a `hard-no` candidate for Phase H.
- **confirm** (recoverable None only): the WHD evidence stands; the mandatory
  Add prescription applies.
- **new-evidence**: short micro-interview, then propose a WHD patch, get the
  user's approval, and apply it NOW with `whd_patch.py` (not deferred to Phase
  H: synthesis's Add prescription must cite WHD text that already exists).
- **reframe**: the user points at existing WHD experience; cite that anchor.

**How an answer changes the row (invariant: `classification` is resume-only).**
`classification` reaches the WHD-blind screen, so WHD-based evidence never
changes it. For new-evidence or reframe, set `whd_evidence` (citing the anchor)
and `recoverable: true`; the row then gets a mandatory Add prescription and
leaves the Gate 1 tally. Change `classification` only when the user shows the
fit step misread evidence that is ON THE RESUME. Synthesis's honesty check can
still label any upgrade a Stretch. Re-validate the gapmap, then run Gate 1.

## Phase C — Gate 1 Gap Brief

A zero-token Python step tallies unrecoverable gaps, checks location, and
evaluates categorical trip rules (never a score cutoff):
```bash
python .claude/skills/resume-fit/helpers/gate1.py <work>/gapmap.yaml --requirements <work>/requirements.yaml --location <work>/location.yaml --preferences <work>/preferences.snapshot.yaml --out <work>/gate1.yaml
```
(Omit `--location` for a remote role.) The tally counts each hard None that is
not recoverable as 1 and each hard Partial that is not recoverable as 0.5; the
Gap Brief lists the two separately. The `location` result is pass,
open-question, trip, or not-evaluated (no preferences file). A location **trip**
trips Gate 1 on its own. A location **open-question** never trips, but
synthesis must carry it into the report's Open Questions (it reads
`gate1.yaml`). If `tripped` is true, present the **Gap Brief** as ONE
structured question with exactly three options. For a location trip, "contest"
means "I would make an exception for this role":

- **(a) Stop** — end the run (`gate1.yaml` is the record).
- **(b) Proceed anyway** — gaps acknowledged; record them in the report's Open
  Questions so the decision is visible.
- **(c) Contest a gap** ("I have evidence for X") — capture the evidence, patch
  the WHD, then update that row the Phase B.5 way, and recompute the tally
  before proceeding.

For each unrecoverable gap, state what filling it would actually require
(experience you don't have vs. a credential vs. pure repositioning) and a
one-line magnitude verdict. The numeric score appears only as a diagnostic line
— the reasoning is the gate. An override is never a shrug: it is either an
accepted risk (b) or new evidence on the record (c).

## Phase D — Screening (WHD-blind by construction)

Build the screening subagent's input from an explicit manifest that OMITS the
WHD, and pass a screening-safe gapmap summary:
```bash
python .claude/skills/resume-fit/helpers/gapmap_summary.py <work>/gapmap.yaml --out <work>/gapmap.summary.yaml
```
Always use `--out`, never a shell `>` redirect (on Windows the redirect can write
a non-UTF-8 file). The summary forwards only the resume-only
`seeker_archetype_resume`; it fails if the gapmap lacks that field.
Dispatch the screening subagent (contract: `contracts/screening.md`) on the
**strong model**, with **no file-read tools** — inputs are: resume,
`requirements.yaml`, `gapmap.summary.yaml`, `scd.yaml`. It writes `<work>/screen.yaml`.

Then validate and run the **canary scan** (fails the run on a blindness leak):
```bash
python .claude/skills/resume-fit/helpers/validate.py <work>/screen.yaml screen
python .claude/skills/resume-fit/helpers/canary.py <work>/screen.yaml <data-plane>/pipeline/whd/<WHD>.md --resume <resume.md>
```
`--resume` also fails the run when the screen's `escalation_quote` is missing or is
not on the resume word for word (`contracts/screening.md` 4b): a quote the recruiter
could not have read is a blindness violation the canary token cannot catch. A figure
in the trigger that is not on the resume is a warning.

Enforcement layers, in order of authority: (1) the dispatch manifest omits the
WHD; (2) the subagent has no file-read tools; (3) the canary token in the WHD
front-matter fails the run if it appears in `screen.yaml`; (4) the prompt
instruction, framing only, never relied on.

## Phase E — Synthesis

The convergence step: the orchestrator, on the **strong model**, reads all
artifacts + the WHD. Spec and verbatim invariants: `contracts/synthesis.md`.

1. Write `<work>/prescriptions.yaml`, then enforce coverage, the one-summary rule
   and the banner rules (decision D1):
   ```bash
   python .claude/skills/resume-fit/helpers/prescriptions.py <work>/prescriptions.yaml <work>/gapmap.yaml <work>/requirements.yaml --resume <resume.md>
   ```
   `--resume` adds the role budget check: every `add`, `cut` and `remove` names its
   `role` (the resume's role heading), and an Add that grows a role past its recency
   bullet budget (5, 4, then 2) must be paired with a Cut or Remove in that role, or
   carry an approved `over_budget_reason`.
2. Assemble the headline numbers deterministically (do not hand-transcribe):
   ```bash
   python .claude/skills/resume-fit/helpers/numbers_strip.py <run>
   ```
3. Before prescribing additions, run the relevance meter and the density checks
   on the seed resume (synthesis §5c, §5d) so prescriptions favor fewer, tighter
   claims. Conditional: if nothing flags, they ask nothing. Run the density lint
   with `--screen <work>/screen.yaml`: if the line that earns a call starts below
   the top two-thirds of page one, prescribe a Reorder that lifts it.
4. Write `<run>/report.md` from `templates/report.md` (verdict-first,
   ~600–900 words, the two triggers quoted verbatim from `screen.yaml`) and
   `<run>/appendix.md` from `templates/appendix.md`.

**Exception-driven interrogation (synthesis):** if the honesty check finds a
load-bearing stretch — a claim that, if withdrawn, flips the Worth-It verdict —
confront it with the user in one question round BEFORE writing the report.

## Phase F — Gate 2

Present `report.md`, then `AskUserQuestion`:
- **Proceed to draft** — enter the finishing loop (Phase G).
- **Stop** — end the run; done.
- **Resolve information gaps first** — answer the report's Open Questions, patch
  the WHD where durable (Phase H), and re-synthesize the affected sections.

## Phase G — Finishing loop

Only after Gate 2 "proceed to draft". Follow `contracts/finishing.md`, which
holds every step, command and invariant. In outline: the summary round (§4b),
the silent tagged draft `<work>/resume_draft.md` (§4, never the deliverable),
the interview rounds until `tags.py` reports clean (§5, §6), the length round,
content first and layout last (§5), one closed-loop re-eval written to
`<work>/reeval.md` (§6b), the render of `<work>/resume_candidate.docx` checked in
Word (§6), the drift check before any edit pass (§2c), and sign-off, which moves
the approved docx to the run's top level under its final name (§7).

## Phase H — WHD reconciliation

Follow `contracts/reconciliation.md`: accumulate the patch queue during synthesis
and finishing, keep only durable items, micro-interview each Stretch / Hard No,
write `<work>/patches.yaml`, let the user dispose each patch, then apply:
```bash
python .claude/skills/resume-fit/helpers/whd_patch.py <data-plane>/pipeline/whd/<WHD>.md <work>/patches.yaml
```

## Hard-no review mode

Invoked on demand (e.g. `/resume-fit review-hard-nos`) or from the Phase A
reminder. Nobody can be expected to remember every hard-no, so the helper lists
them:
```bash
python .claude/skills/resume-fit/helpers/hard_nos.py <data-plane>/pipeline/whd/<WHD>.md
```
Walk every marker (oldest first) in batched AskUserQuestion rounds:
- **Still true**: a `correction` patch refreshes its `(confirmed <date>)`.
- **Now have evidence**: capture it and propose an evidence patch plus a
  `correction` that removes the marker line's claim.
- **Remove**: a `correction` that replaces the marker line with nothing.
Fix any `unparsed` lines first (they are markers a typo hid). Apply approved
patches with `whd_patch.py`, then record the review:
```bash
python .claude/skills/resume-fit/helpers/hard_nos.py mark-reviewed <data-plane>/pipeline/whd/<WHD>.md
```
Also run this review as part of a full WHD rebuild after a major life change.

## Deterministic helpers (never spend a token)

All are pure Python in `helpers/`, invoked via bash and unit-tested (`tests/`).
They own the arithmetic and string-matching so the model never does. Each one's
docstring and `-h` give its full rules and options; the phase text above and
the contracts show where each runs.

| Phase | Helpers |
|---|---|
| Setup | `config.py`, `whd_migrate.py`, `canary.py init`, `env_check.py` (read-only readiness report) |
| A | `runfolder.py`, `validate.py` (schemas: requirements, location, preferences, scd, gapmap, screen, prescriptions, patches, summary_options), `hard_nos.py` |
| B.5, C | `gap_review.py`, `gate1.py` (uses `location_gate.py`, `score.py`) |
| D | `gapmap_summary.py`, `canary.py` (with `verbatim.py` for the escalation quote) |
| E | `prescriptions.py`, `numbers_strip.py`, `relevance.py`, `whitespace_check.py`, `density_lint.py`, `ats.py` |
| G | `summary_lint.py`, `chrono_check.py`, `tags.py`, `length_budget.py`, `compress_candidates.py`, `ats_chars.py`, `render_docx.py` (renders, cleans metadata, saves through Word), `word_pages.py` (Word page count), `docx_drift.py` |
| H | `whd_patch.py` (backs up the WHD first), `whd_anchors.py`, `whd_io.py` |
| Standalone, not in the loop | `structure_lint.py`, `contact_check.py`, `filesize_gate.py` |

Open work and decisions: `../TODO.md`.
