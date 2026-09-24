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

Collapses a five-prompt, two-model, copy-paste pipeline into one skill. Given a
job description, it produces one concise report and — when warranted — a
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

The data-plane path is resolved by `helpers/config.py`, in order:
1. `$RESUME_FIT_DATA_PLANE`
2. `$XDG_CONFIG_HOME/resume-fit/config.yaml` (or `~/.config/resume-fit/config.yaml`)

On first run, if neither is set, ask the user where their data plane lives (a
private folder, e.g. `.../resume-pipeline-data`) and persist it:

```bash
python .claude/skills/resume-fit/helpers/config.py set "/path/to/data-plane"
```

The data plane must contain `pipeline/whd/<the WHD>.md`. A new user with no WHD
goes through onboarding first (see Build status → not yet built).

The WHD needs a unique canary token for the screening leak check. Generate it
once (safe to re-run; an existing real token is kept):

```bash
python .claude/skills/resume-fit/helpers/canary.py init <data-plane>/pipeline/whd/<WHD>.md
```

`canary.py` refuses to scan while the template placeholder is still in place.

## Architecture (plan section 2)

```
Phase A  INTAKE (orchestrator)         -> requirements.yaml, run folder   [BUILT]
Phase B  PARALLEL research + fit        -> scd.yaml, gapmap.yaml           [BUILT]
Phase C  GATE 1 Gap Brief (3 options)   -> Python tally + trip rules       [BUILT]
Phase D  SCREENING (WHD-blind)          -> screen.yaml                     [BUILT]
Phase E  SYNTHESIS                       -> report.md + appendix.md         [BUILT]
Phase F  GATE 2 user decision                                              [BUILT]
Phase G  FINISHING LOOP                  -> resume_candidate.docx (then final)  [BUILT]
Phase H  WHD RECONCILIATION              -> WHD patched                     [BUILT]
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

## Phase A — Intake (BUILT)

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
   # -> <data-plane>/pipeline/runs/<company>-<role>-<date>/
   ```
   Write `requirements.yaml` into it. The helper also snapshots
   `<data-plane>/pipeline/whd/preferences.yaml` (the candidate's deal-breaker
   rules; template: `templates/preferences-template.yaml`) into the run as
   `preferences.snapshot.yaml`.
4. **Location assessment** (skip for a remote role): judge the geography and
   write `<run>/location.yaml` (`schemas/location.schema.yaml`):
   `drive_minutes_from_home` (from the preferences `home`), `nearest_metro` (an
   exact name from the preferences `relocation.metros`, or null),
   `metro_minutes` (drive from that metro's core), `borderline` (true for a
   genuine edge case), and a one-line `notes`. Estimate drive times from
   general knowledge; no maps API. Thresholds are NOT applied here: Gate 1
   applies them from the preferences file.
5. **Validate before proceeding** (structural drift fails loudly here):
   ```bash
   python .claude/skills/resume-fit/helpers/validate.py <run>/requirements.yaml requirements
   python .claude/skills/resume-fit/helpers/validate.py <run>/location.yaml location   # non-remote roles only
   ```
6. **Hard-no reminder** (one line, never blocks):
   ```bash
   python .claude/skills/resume-fit/helpers/hard_nos.py <data-plane>/pipeline/whd/<WHD>.md
   ```
   If `review_due` is true, say once: "Your hard-no list was last reviewed
   <last_review or never> (<marker_count> markers). Run the hard-no review now
   or skip?" See **Hard-no review mode** below. Keep the `stale` list for
   synthesis.

## Phase B — Parallel research + fit (BUILT)

Dispatch two subagents concurrently on the **cheap/fast model**. Each receives a
minimal manifest — the fit subagent never sees the SCD; the research subagent
never sees the resume or WHD.

- **Research subagent** — contract: `contracts/research.md`. Manifest:
  `requirements.yaml` (company/role) + web search. Writes `scd.yaml`.
- **Fit subagent** — contract: `contracts/fit.md`. Manifest: `requirements.yaml`
  + the resume + the WHD. Writes `gapmap.yaml`.

Validate both on return (fail loudly, not silently downstream):
```bash
python .claude/skills/resume-fit/helpers/validate.py <run>/scd.yaml scd
python .claude/skills/resume-fit/helpers/validate.py <run>/gapmap.yaml gapmap
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
python .claude/skills/resume-fit/helpers/gap_review.py <run>/gapmap.yaml <run>/requirements.yaml
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

## Phase C — Gate 1 Gap Brief (BUILT)

A zero-token Python step tallies unrecoverable gaps, checks location, and
evaluates categorical trip rules (never a score cutoff):
```bash
python .claude/skills/resume-fit/helpers/gate1.py <run>/gapmap.yaml --requirements <run>/requirements.yaml --location <run>/location.yaml --preferences <run>/preferences.snapshot.yaml --out <run>/gate1.yaml
```
(Omit `--location` for a remote role.) The tally counts each hard None that is
not recoverable as 1 and each hard Partial that is not recoverable as 0.5; the
Gap Brief lists the two separately. The `location` result is pass,
open-question, trip, or not-evaluated (no preferences file). A location **trip**
trips Gate 1 on its own. A location **open-question** never trips, but
synthesis must carry it into the report's Open Questions (it reads
`gate1.yaml`). If `tripped` is true, present the **Gap Brief** as ONE
structured question with exactly three options (fixed format: plan section 2,
Phase C). For a location trip, "contest" means "I would make an exception for
this role":

- **(a) Stop** — archive the Gap Brief to the run folder and end the run.
- **(b) Proceed anyway** — gaps acknowledged; record them in the report's Open
  Questions so the decision is visible.
- **(c) Contest a gap** ("I have evidence for X") — route immediately into the
  Phase H micro-interview: capture the evidence, patch the WHD, then update that
  row the Phase B.5 way (set `whd_evidence` + `recoverable: true`; never change
  the resume-only `classification` for WHD evidence), and recompute the tally
  before proceeding.

For each unrecoverable gap, state what filling it would actually require
(experience you don't have vs. a credential vs. pure repositioning) and a
one-line magnitude verdict. The numeric score appears only as a diagnostic line
— the reasoning is the gate. An override is never a shrug: it is either an
accepted risk (b) or new evidence on the record (c).

## Phase D — Screening (BUILT, WHD-blind by construction)

Build the screening subagent's input from an explicit manifest that OMITS the
WHD, and pass a screening-safe gapmap summary:
```bash
python .claude/skills/resume-fit/helpers/gapmap_summary.py <run>/gapmap.yaml --out <run>/gapmap.summary.yaml
```
Always use `--out`, never a shell `>` redirect (on Windows the redirect can write
a non-UTF-8 file). The summary forwards only the resume-only
`seeker_archetype_resume`; it fails if the gapmap lacks that field.
Dispatch the screening subagent (contract: `contracts/screening.md`) on the
**strong model**, with **no file-read tools** — inputs are: resume,
`requirements.yaml`, `gapmap.summary.yaml`, `scd.yaml`. It writes `screen.yaml`.

Then validate and run the **canary scan** (fails the run on a blindness leak):
```bash
python .claude/skills/resume-fit/helpers/validate.py <run>/screen.yaml screen
python .claude/skills/resume-fit/helpers/canary.py <run>/screen.yaml <data-plane>/pipeline/whd/<WHD>.md
```

## Phase E — Synthesis (BUILT)

The convergence step: the orchestrator, on the **strong model**, reads all
artifacts + the WHD and produces the report. Spec + verbatim Stage 3 invariants:
`contracts/synthesis.md`. Steps:

1. Produce `prescriptions.yaml` (validated against `schemas/prescriptions.schema.yaml`),
   then enforce the mandatory rule — every Recoverable Gap has a covering Add
   prescription with a WHD source:
   ```bash
   python .claude/skills/resume-fit/helpers/prescriptions.py <run>/prescriptions.yaml <run>/gapmap.yaml
   ```
2. Assemble the headline numbers deterministically (do not hand-transcribe):
   ```bash
   python .claude/skills/resume-fit/helpers/numbers_strip.py <run>
   ```
3. Write `report.md` from `templates/report.md` — verdict-first, ~600–900 words.
   The two triggers are quoted **verbatim** from `screen.yaml`. Write everything
   auditable-but-not-headline (score math, full Gap Map, persona reasoning,
   competitive comparison) to `appendix.md` from `templates/appendix.md`.
4. **Relevance coverage (before length):** run the inverse meter to flag resume
   claims with zero linkage to THIS JD (per-JD, value-blind):
   ```bash
   python .claude/skills/resume-fit/helpers/relevance.py <resume.md> <run>/requirements.yaml <run>/gapmap.yaml
   ```
   The model splits the `none`-linkage set into dead-weight vs differentiator vs
   structural (`contracts/synthesis.md` §5c); the user ratifies before any
   Compress/Cut. Prune for value here, before the Phase G length round. Conditional
   — if nothing flags `none`, this asks nothing.
5. **Density check (before writing full prose):** run the readability check so
   synthesis can favor tighter phrasing from the start instead of brute-force
   cuts later (`contracts/synthesis.md` §5d):
   ```bash
   python .claude/skills/resume-fit/helpers/whitespace_check.py <resume.md> --margin 0.6
   ```
   Per-page fullness is approximate (verify the real docx by eye) but the raw
   word/char counts are independently checkable. This is a layout/readability
   signal, NOT a bullet-length-uniformity nudge — uniform length is itself an
   AI-writing tell, so never normalize bullets toward this resume's own median.

**Exception-driven interrogation (synthesis):** if the honesty check finds a
load-bearing stretch — a claim that, if withdrawn, flips the Worth-It verdict —
confront it with the user in one question round BEFORE writing the report.

## Phase F — Gate 2 (BUILT)

Present `report.md`, then `AskUserQuestion`:
- **Proceed to draft** — enter the finishing loop (Phase G).
- **Stop** — archive the run; done.
- **Resolve information gaps first** — answer the report's Open Questions, patch
  the WHD where durable (Phase H), and re-synthesize the affected sections.

## Phase G — Finishing loop (BUILT)

Only after Gate 2 "proceed to draft". Contract + verbatim ghost-editor invariants:
`contracts/finishing.md`. The tagged draft is a **worklist, never the deliverable**.

1. Generate the silent tagged draft (`resume_draft.md`) applying only the
   `prescriptions.yaml` edits, in the candidate's voice (WHD `voice-sample`).
   Target 2 pages; apply any Compress/Cut prescriptions as you draft. Keep every
   section newest-first, then confirm (`contracts/finishing.md` §2b):
   ```bash
   python .claude/skills/resume-fit/helpers/chrono_check.py <run>/resume_draft.md
   ```
2. Run the finishing loop: batched AskUserQuestion rounds (Supply / Keyword /
   Voice / Stretch / **Length**), highest-stakes first, ~3 per type.
3. Gate on the tag exit-check every pass:
   ```bash
   python .claude/skills/resume-fit/helpers/tags.py <run>/resume_draft.md
   ```
   Loop until it reports `clean` (zero blocking tags). If the user stalls, save
   with a NOT SUBMITTABLE banner — never render a tagged draft.
4. Length round — check the page budget (advisory, 2-page default):
   ```bash
   python .claude/skills/resume-fit/helpers/length_budget.py <run>/resume_draft.md --max-pages 2
   ```
   If over budget, show the user the per-section **cost** (from this helper) beside
   the per-section **value** (JD-linkage from `gapmap.yaml`/`screen.yaml`) and let
   them decide cuts — protect JD-relevant/recent-in-demand work, cut cheap inches
   first (oldest unlinked roles, tail sections). Never auto-truncate. Survey EVERY
   section: record keep / compress / cut for each heading in the helper's
   `review_checklist` into `<run>/length_review.yaml`, and re-run with
   `--review <run>/length_review.yaml` until `review.complete` is true before
   cutting or overriding. Prefer
   compression over cutting: `python .claude/skills/resume-fit/helpers/compress_candidates.py
   <run>/resume_draft.md` finds 3+ item lists mechanically; the model proposes an
   accurate count+category phrase and the user ratifies before it's applied. If
   the user chooses to exceed 2 pages, record the reason in
   `<run>/length_override.md`. Re-run until it reports `fits` OR an override
   reason is recorded.
5. Closed-loop re-eval (ONE pass, before promoting the draft) — validate the clean
   tagged draft on the same axes as the seed (`contracts/finishing.md` §6b):
   ```bash
   python .claude/skills/resume-fit/helpers/ats.py <run>/requirements.yaml <run>/resume_draft.md
   python .claude/skills/resume-fit/helpers/relevance.py <run>/resume_draft.md <run>/requirements.yaml <run>/gapmap.yaml
   python .claude/skills/resume-fit/helpers/ats_chars.py <run>/resume_draft.md
   python .claude/skills/resume-fit/helpers/chrono_check.py <run>/resume_draft.md
   ```
   Confirm ATS coverage didn't regress vs seed, no NEW `none`-linkage claim was
   introduced, the voice check passed, `ats_chars.py` reports **clean** (fixed
   rule — em/en dashes, curly quotes, decorative bullets, emoji; never tolerated,
   not just a regression check), and `chrono_check.py` reports `ordered`. Write `reeval.md`. No recursion: any issue
   surfaces as one yes/no, not a new trim loop.
6. On clean + length-resolved + re-eval clean, write `resume_candidate.md` and
   render an ATS-safe docx (0.6in margins, single column, no tables):
   ```bash
   python .claude/skills/resume-fit/helpers/render_docx.py <run>/resume_candidate.md <run>/resume_candidate.docx
   ```
   Deliverables: `resume_candidate.docx` + `resume_candidate.md`. **Not yet
   "final"** — see Phase G §7 in `contracts/finishing.md`: the user reads it
   aloud and explicitly approves before a true final is named. The input resume
   is never renamed regardless of what the user originally called it. On
   approval, the true final deliverable is rendered as
   `<LASTNAME>_<FIRSTNAME>_<COMPANY>_<DATE>.docx` — the one filename in the
   pipeline meant for a human, not another pipeline step.
7. **The user may edit the `.docx` directly.** Before any further edit pass and
   before the final render, check for drift (`contracts/finishing.md` §2c):
   ```bash
   python .claude/skills/resume-fit/helpers/docx_drift.py <run>/resume_candidate.md <run>/resume_candidate.docx
   ```
   On DRIFT, rebuild with `--pull <run>/resume_candidate.pulled.md`, show the user
   the diff, and on confirmation make it the new `resume_candidate.md`.

## Phase H — WHD reconciliation (BUILT)

Interactive; makes each run improve the standing WHD. Contract:
`contracts/reconciliation.md`.

1. Accumulate a patch queue during synthesis + finishing (new facts, corrections,
   evidence for Partials, information-gap answers).
2. Classify each: WHD-worthy (durable) vs. application-specific. Only durable
   items become proposed patches.
3. Micro-interview each Stretch / Hard No: "Do you have real evidence for X?" —
   yes → capture as evidence (may upgrade Stretch→Genuine next run); no → write a
   `hard-no: X (confirmed <date>)` marker so future runs don't re-litigate it.
4. Write `patches.yaml` (validated against `schemas/patches.schema.yaml`), present
   each as a diff (AskUserQuestion per patch or batch-approve), then apply only
   the approved + durable ones:
   ```bash
   python .claude/skills/resume-fit/helpers/whd_patch.py <data-plane>/pipeline/whd/<WHD>.md <run>/patches.yaml
   ```
   Appends to anchored sections + writes changelog entries. A `correction`
   patch instead REPLACES its `old` text (which must occur exactly once in the
   target section) with `content`, logging old and new in the changelog; the
   helper reports other sections that still hold the old text, so propose
   corrections there too. The Voice Sample and changelog are never patch
   targets; the user ratifies every patch.

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

All are pure Python, invoked via bash, unit-tested (`tests/`). They own the
arithmetic and string-matching so the model never does.

| Helper | Purpose | CLI |
|---|---|---|
| `config.py` | Resolve/persist the data-plane path | `config.py [set <path>]` |
| `runfolder.py` | Create a run folder | `runfolder.py "<Company>" "<Role>"` |
| `validate.py` | Validate an artifact against a schema | `validate.py <file.yaml> <schema>` |
| `score.py` | Weighted score from gapmap | `score.py <gapmap.yaml>` |
| `ats.py` | Exact-match keyword scan (synonym-aware) | `ats.py <requirements.yaml> <resume>` |
| `gate1.py` | Weighted gap tally (weak Partial = 0.5) + location check + trip rules | `gate1.py <gapmap.yaml> [--requirements R --location L --preferences P] [--out F]` |
| `location_gate.py` | Location rules: JD facts x model geography x preferences thresholds | (called by `gate1.py`) |
| `gap_review.py` | Rows for the Phase B.5 gap review (every None + weak Partials) | `gap_review.py <gapmap.yaml> [<requirements.yaml>]` |
| `hard_nos.py` | List hard-no markers with age; `mark-reviewed` records a full review | `hard_nos.py <whd.md>` / `hard_nos.py mark-reviewed <whd.md>` |
| `whd_anchors.py` | Resolve a WHD section by anchor id | `whd_anchors.py <whd.md> <anchor>` |
| `gapmap_summary.py` | Screening-safe gapmap (strips WHD fields, resume-only archetype) | `gapmap_summary.py <gapmap.yaml> --out <file>` |
| `canary.py` | Screening-blindness leak scan; `init` writes a unique token | `canary.py <screen.yaml> <whd.md>` / `canary.py init <whd.md>` |
| `numbers_strip.py` | Deterministic report headline numbers | `numbers_strip.py <run>` |
| `prescriptions.py` | Enforce every recoverable gap has an Add row; reject "X or Y" targets | `prescriptions.py <prescriptions.yaml> <gapmap.yaml>` |
| `tags.py` | Finishing-loop tag scan + exit check | `tags.py <resume_draft.md>` |
| `length_budget.py` | Advisory 2-page estimator + per-section cost breakdown + review completeness | `length_budget.py <resume.md> --max-pages 2 [--review <length_review.yaml>]` |
| `chrono_check.py` | Newest-first ordering check per section | `chrono_check.py <resume.md>` |
| `docx_drift.py` | Detect hand edits in the `.docx` the `.md` lacks; `--pull` rebuilds md | `docx_drift.py <resume.md> <resume.docx> [--pull <out.md>]` |
| `relevance.py` | Line-level JD-relevance meter (per-JD, value-blind); flags `none`-linkage claims | `relevance.py <resume.md> <requirements.yaml> <gapmap.yaml>` |
| `ats_chars.py` | Scans for ATS-unsafe characters (em/en dash, curly quotes, decorative bullets, emoji, prose "&") | `ats_chars.py <resume.md>` |
| `compress_candidates.py` | Finds 3+ item lists as compression candidates (pattern only, no category-word suggestion) | `compress_candidates.py <resume.md>` |
| `whitespace_check.py` | Per-page fullness/density check (research-grounded readability, not bullet-uniformity) | `whitespace_check.py <resume.md> --margin 0.6` |
| `render_docx.py` | Render clean markdown to an ATS-safe docx (0.6in) | `render_docx.py <resume_candidate.md> <out.docx>` |
| `whd_patch.py` | Apply approved WHD patches (append, or `correction` = replace) + changelog | `whd_patch.py <whd.md> <patches.yaml>` |

Schema names for `validate.py`: `requirements`, `location`, `preferences`, `scd`, `gapmap`, `screen`, `prescriptions`, `patches`.

## Screening-blindness enforcement (BUILT)

Enforcement layers, in order of authority:
1. **Dispatch construction** — the screening subagent's input is built from an
   explicit manifest that omits the WHD.
2. **Tool restriction** — the screening subagent gets no file-read tools; all
   inputs arrive inline, so it cannot go find the WHD.
3. **Canary check** — a unique token in the WHD front-matter (`canary:`); a
   deterministic post-run scan fails the run if it appears in `screen.yaml`.
4. **Prompt instruction** — framing only; never relied on for enforcement.

## Build status

- **Built (Phases 1–4):** WHD restructure + template; data-plane config;
  run-folder convention; artifact schemas; all deterministic helpers with tests;
  synthetic `examples/` fixture (now a complete end-to-end run incl.
  prescriptions/report/appendix); Phase A intake; the four contracts
  (`contracts/` — research, fit, screening, synthesis) ported from the v1 FINAL
  prompts with verbatim invariants; Phase B parallel dispatch + exception
  triggers; Phase C Gate 1 three-option interrogation; Phase D screening with
  full blindness enforcement; Phase E synthesis (prescriptions coverage +
  deterministic numbers strip + report/appendix templates); Phase F Gate 2.
- **Also built (Phase 5):** finishing-loop contract (`contracts/finishing.md`)
  with verbatim ghost-editor invariants; Phase G loop mechanics; `tags.py` exit
  gate; `render_docx.py` ATS-safe render.
- **Also built (Phase 6):** reconciliation contract (`contracts/reconciliation.md`);
  Phase H loop; `patches.yaml` schema; `whd_patch.py` (propose/dispose apply +
  changelog; Voice Sample never edited).
- **All eight phases (A–H) are built.** Remaining: Phase 7 validation replay and
  the public-release backlog (onboarding mode for new users, README rewrite,
  strip incidental personal references from docs) — see `../TODO.md`.

See `../TODO.md` and the v2 plan of work for the full sequence.
