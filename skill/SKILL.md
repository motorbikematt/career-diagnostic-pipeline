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
Phase B  PARALLEL research + fit        -> scd.yaml, gapmap.yaml           [Phase 3]
Phase C  GATE 1 Gap Brief (3 options)   -> Python tally + trip rules       [helper BUILT; wiring Phase 3]
Phase D  SCREENING (WHD-blind)          -> screen.yaml                     [Phase 3]
Phase E  SYNTHESIS                       -> report.md + appendix.md         [Phase 4]
Phase F  GATE 2 user decision                                              [Phase 4]
Phase G  FINISHING LOOP                  -> resume_final.docx               [Phase 5]
Phase H  WHD RECONCILIATION              -> WHD patched                     [Phase 6]
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

## Deterministic helpers (never spend a token)

All are pure Python, invoked via bash, unit-tested (`tests/`). They own the
arithmetic and string-matching so the model never does.

| Helper | Purpose | CLI |
|---|---|---|
| `config.py` | Resolve/persist the data-plane path | `config.py [set <path>]` |
| `runfolder.py` | Create a run folder | `runfolder.py "<Company>" "<Role>"` |
| `validate.py` | Validate an artifact against a schema | `validate.py <file.yaml> <schema>` |
| `score.py` | Weighted score from gapmap | `score.py <gapmap.yaml>` |
| `ats.py` | Exact-match keyword scan | `ats.py <requirements.yaml> <resume>` |
| `gate1.py` | Unrecoverable-gap tally + trip rules | `gate1.py <gapmap.yaml>` |
| `whd_anchors.py` | Resolve a WHD section by anchor id | `whd_anchors.py <whd.md> <anchor>` |

Schema names for `validate.py`: `requirements`, `scd`, `gapmap`, `screen`.

## Screening-blindness enforcement (design; wired in Phase 3)

Enforcement layers, in order of authority:
1. **Dispatch construction** — the screening subagent's input is built from an
   explicit manifest that omits the WHD.
2. **Tool restriction** — the screening subagent gets no file-read tools; all
   inputs arrive inline, so it cannot go find the WHD.
3. **Canary check** — a unique token in the WHD front-matter (`canary:`); a
   deterministic post-run scan fails the run if it appears in `screen.yaml`.
4. **Prompt instruction** — framing only; never relied on for enforcement.

## Build status

- **Built (Phases 1–2):** WHD restructure + template; data-plane config;
  run-folder convention; artifact schemas; all deterministic helpers with tests;
  synthetic `examples/` fixture; Phase A intake.
- **Not yet built:** Phase B subagent contracts + parallel dispatch (Phase 3),
  Gate 1 wiring + interrogation (Phase 3), screening subagent + canary wiring
  (Phase 3), synthesis + report/appendix templates (Phase 4), finishing loop +
  docx (Phase 5), WHD reconciliation (Phase 6), onboarding mode for new users
  (public release backlog).

See `../TODO.md` and the v2 plan of work for the full sequence.
