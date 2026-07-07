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
python skill/helpers/config.py set "/path/to/data-plane"
```

The data plane must contain `pipeline/whd/<the WHD>.md`. A new user with no WHD
goes through onboarding first (see Build status → not yet built).

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
   recruiter-persona cues.
3. **Create the run folder:**
   ```bash
   python skill/helpers/runfolder.py "<Company>" "<Role>"
   # -> <data-plane>/pipeline/runs/<company>-<role>-<date>/
   ```
   Write `requirements.yaml` into it.
4. **Validate before proceeding** (structural drift fails loudly here):
   ```bash
   python skill/helpers/validate.py <run>/requirements.yaml requirements
   ```

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
python skill/helpers/validate.py <run>/scd.yaml scd
python skill/helpers/validate.py <run>/gapmap.yaml gapmap
```

**Exception-driven interrogation (fire only on FUNDAMENTAL mismatches):**
- *Fit:* Seeker vs. JD archetype structurally incompatible → ask whether
  repositioning is intended before screening simulates the wrong candidate.
- *Research:* SCD contradicts the resume's positioning, or surfaces something
  that changes whether the user wants the job (layoffs, acquisition, leadership
  exodus) → surface now, not in the report.

One question round each; overflow to a punch list. Routine gaps wait for their phase.

## Phase C — Gate 1 Gap Brief (BUILT)

A zero-token Python step tallies unrecoverable gaps and evaluates categorical
trip rules (never a score cutoff):
```bash
python skill/helpers/gate1.py <run>/gapmap.yaml
```
If `tripped` is true, present the **Gap Brief** as ONE structured question with
exactly three options (fixed format — plan section 2, Phase C):

- **(a) Stop** — archive the Gap Brief to the run folder and end the run.
- **(b) Proceed anyway** — gaps acknowledged; record them in the report's Open
  Questions so the decision is visible.
- **(c) Contest a gap** ("I have evidence for X") — route immediately into the
  Phase H micro-interview: capture the evidence, patch the WHD, re-run the fit
  classification for that requirement, and recompute the tally before proceeding.

For each unrecoverable gap, state what filling it would actually require
(experience you don't have vs. a credential vs. pure repositioning) and a
one-line magnitude verdict. The numeric score appears only as a diagnostic line
— the reasoning is the gate. An override is never a shrug: it is either an
accepted risk (b) or new evidence on the record (c).

## Phase D — Screening (BUILT, WHD-blind by construction)

Build the screening subagent's input from an explicit manifest that OMITS the
WHD, and pass a screening-safe gapmap summary:
```bash
python skill/helpers/gapmap_summary.py <run>/gapmap.yaml > <run>/gapmap.summary.yaml
```
Dispatch the screening subagent (contract: `contracts/screening.md`) on the
**strong model**, with **no file-read tools** — inputs are: resume,
`requirements.yaml`, `gapmap.summary.yaml`, `scd.yaml`. It writes `screen.yaml`.

Then validate and run the **canary scan** (fails the run on a blindness leak):
```bash
python skill/helpers/validate.py <run>/screen.yaml screen
python skill/helpers/canary.py <run>/screen.yaml <data-plane>/pipeline/whd/<WHD>.md
```

## Phase E — Synthesis (BUILT)

The convergence step: the orchestrator, on the **strong model**, reads all
artifacts + the WHD and produces the report. Spec + verbatim Stage 3 invariants:
`contracts/synthesis.md`. Steps:

1. Produce `prescriptions.yaml` (validated against `schemas/prescriptions.schema.yaml`),
   then enforce the mandatory rule — every Recoverable Gap has a covering Add
   prescription with a WHD source:
   ```bash
   python skill/helpers/prescriptions.py <run>/prescriptions.yaml <run>/gapmap.yaml
   ```
2. Assemble the headline numbers deterministically (do not hand-transcribe):
   ```bash
   python skill/helpers/numbers_strip.py <run>
   ```
3. Write `report.md` from `templates/report.md` — verdict-first, ~600–900 words.
   The two triggers are quoted **verbatim** from `screen.yaml`. Write everything
   auditable-but-not-headline (score math, full Gap Map, persona reasoning,
   competitive comparison) to `appendix.md` from `templates/appendix.md`.
4. **Relevance coverage (before length):** run the inverse meter to flag resume
   claims with zero linkage to THIS JD (per-JD, value-blind):
   ```bash
   python skill/helpers/relevance.py <resume.md> <run>/requirements.yaml <run>/gapmap.yaml
   ```
   The model splits the `none`-linkage set into dead-weight vs differentiator vs
   structural (`contracts/synthesis.md` §5c); the user ratifies before any
   Compress/Cut. Prune for value here, before the Phase G length round. Conditional
   — if nothing flags `none`, this asks nothing.
5. **Density check (before writing full prose):** run the readability check so
   synthesis can favor tighter phrasing from the start instead of brute-force
   cuts later (`contracts/synthesis.md` §5d):
   ```bash
   python skill/helpers/whitespace_check.py <resume.md> --margin 0.6
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
   Target 2 pages; apply any Compress/Cut prescriptions as you draft.
2. Run the finishing loop: batched AskUserQuestion rounds (Supply / Keyword /
   Voice / Stretch / **Length**), highest-stakes first, ~3 per type.
3. Gate on the tag exit-check every pass:
   ```bash
   python skill/helpers/tags.py <run>/resume_draft.md
   ```
   Loop until it reports `clean` (zero blocking tags). If the user stalls, save
   with a NOT SUBMITTABLE banner — never render a tagged draft.
4. Length round — check the page budget (advisory, 2-page default):
   ```bash
   python skill/helpers/length_budget.py <run>/resume_draft.md --max-pages 2
   ```
   If over budget, show the user the per-section **cost** (from this helper) beside
   the per-section **value** (JD-linkage from `gapmap.yaml`/`screen.yaml`) and let
   them decide cuts — protect JD-relevant/recent-in-demand work, cut cheap inches
   first (oldest unlinked roles, tail sections). Never auto-truncate. Prefer
   compression over cutting: `python skill/helpers/compress_candidates.py
   <run>/resume_draft.md` finds 3+ item lists mechanically; the model proposes an
   accurate count+category phrase and the user ratifies before it's applied. If
   the user chooses to exceed 2 pages, record the reason in
   `<run>/length_override.md`. Re-run until it reports `fits` OR an override
   reason is recorded.
5. Closed-loop re-eval (ONE pass, before promoting the draft) — validate the clean
   tagged draft on the same axes as the seed (`contracts/finishing.md` §6b):
   ```bash
   python skill/helpers/ats.py <run>/requirements.yaml <run>/resume_draft.md
   python skill/helpers/relevance.py <run>/resume_draft.md <run>/requirements.yaml <run>/gapmap.yaml
   python skill/helpers/ats_chars.py <run>/resume_draft.md
   ```
   Confirm ATS coverage didn't regress vs seed, no NEW `none`-linkage claim was
   introduced, the voice check passed, and `ats_chars.py` reports **clean** (fixed
   rule — em/en dashes, curly quotes, decorative bullets, emoji; never tolerated,
   not just a regression check). Write `reeval.md`. No recursion — any issue
   surfaces as one yes/no, not a new trim loop.
6. On clean + length-resolved + re-eval clean, write `resume_candidate.md` and
   render an ATS-safe docx (0.6in margins, single column, no tables):
   ```bash
   python skill/helpers/render_docx.py <run>/resume_candidate.md <run>/resume_candidate.docx
   ```
   Deliverables: `resume_candidate.docx` + `resume_candidate.md`. **Not yet
   "final"** — see Phase G §7 in `contracts/finishing.md`: the user reads it
   aloud and explicitly approves before a true final is named. The input resume
   is never renamed regardless of what the user originally called it. On
   approval, the true final deliverable is rendered as
   `<LASTNAME>_<FIRSTNAME>_<COMPANY>_<DATE>.docx` — the one filename in the
   pipeline meant for a human, not another pipeline step.

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
   python skill/helpers/whd_patch.py <data-plane>/pipeline/whd/<WHD>.md <run>/patches.yaml
   ```
   Appends to anchored sections + writes changelog entries. The Voice Sample is
   never edited; the user ratifies every patch.

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
| `gate1.py` | Unrecoverable-gap tally + trip rules | `gate1.py <gapmap.yaml>` |
| `whd_anchors.py` | Resolve a WHD section by anchor id | `whd_anchors.py <whd.md> <anchor>` |
| `gapmap_summary.py` | Screening-safe gapmap (strips WHD fields) | `gapmap_summary.py <gapmap.yaml>` |
| `canary.py` | Screening-blindness leak scan | `canary.py <screen.yaml> <whd.md>` |
| `numbers_strip.py` | Deterministic report headline numbers | `numbers_strip.py <run>` |
| `prescriptions.py` | Enforce every recoverable gap has an Add row | `prescriptions.py <prescriptions.yaml> <gapmap.yaml>` |
| `tags.py` | Finishing-loop tag scan + exit check | `tags.py <resume_draft.md>` |
| `length_budget.py` | Advisory 2-page estimator + per-section cost breakdown | `length_budget.py <resume.md> --max-pages 2` |
| `relevance.py` | Line-level JD-relevance meter (per-JD, value-blind); flags `none`-linkage claims | `relevance.py <resume.md> <requirements.yaml> <gapmap.yaml>` |
| `ats_chars.py` | Scans for ATS-unsafe characters (em/en dash, curly quotes, decorative bullets, emoji, prose "&") | `ats_chars.py <resume.md>` |
| `compress_candidates.py` | Finds 3+ item lists as compression candidates (pattern only, no category-word suggestion) | `compress_candidates.py <resume.md>` |
| `whitespace_check.py` | Per-page fullness/density check (research-grounded readability, not bullet-uniformity) | `whitespace_check.py <resume.md> --margin 0.6` |
| `render_docx.py` | Render clean markdown to an ATS-safe docx (0.6in) | `render_docx.py <resume_candidate.md> <out.docx>` |
| `whd_patch.py` | Apply approved WHD patches + changelog | `whd_patch.py <whd.md> <patches.yaml>` |

Schema names for `validate.py`: `requirements`, `scd`, `gapmap`, `screen`, `prescriptions`, `patches`.

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
