# Reconciliation (orchestrator step, Phase H)

New in v2 (plan section 6) — closes the loop the v1 flow left open (it flagged a
discrepancy and left you to re-run the Pre-Stage interview by hand). Interactive,
run by the orchestrator. Net effect: every application run makes the standing WHD
more complete and more honest, and the Recoverable Gaps count should trend down
across runs.

## 1. Role
Reconcile the WHD from the run's accumulated patch queue — propose durable
improvements, the user ratifies each, apply with changelog entries.

## 2. Invariants (plan section 6 — DO NOT weaken)
- **Propose, don't apply.** Patches are presented as a diff against the anchored
  WHD sections (AskUserQuestion per patch or batch-approve). Approved patches are
  applied with changelog entries; rejected ones are dropped. The WHD's
  validation-pass ethos ("is anything overstated?") is preserved because the user
  ratifies every edit.
- **Classify each item** WHD-worthy (durable fact about your history) vs.
  application-specific (framing for this employer only). ONLY the former is
  proposed as a patch (`whd_worthy: true`).
- **Micro-interview on discrepancies.** For each Stretch or Hard No the synthesis
  flagged: one targeted question — "Do you have real evidence for X?" If yes, the
  evidence is captured into the relevant WHD section, and X may upgrade from
  Stretch to Genuine in future runs. If no, a `hard-no: X (confirmed <date>)`
  marker is written so future runs don't re-litigate it. This is the honesty
  check compounding instead of repeating.
- **The Voice Sample is never edited** (anchor `voice-sample`).
- **Full Pre-Stage retained** for genuinely new roles or major life changes —
  reconciliation handles increments, not rebuilds.

## 3. Input manifest
The run's patch queue accumulated during synthesis + finishing (new facts,
corrections, evidence surfaced for Partials, information-gap answers), the
`gapmap.yaml` (which items were Stretch/Hard No), and the WHD (anchored).

## 4. Output
- **`patches.yaml`** (validated against `schemas/patches.schema.yaml`): each item
  {kind, target_anchor, content, whd_worthy, status, note, prompted_by}.
- After the user disposes each patch, apply the approved+durable ones:
  ```bash
  python skill/helpers/whd_patch.py <data-plane>/pipeline/whd/<WHD>.md <run>/patches.yaml
  ```
  This appends content to the anchored sections and writes date-stamped changelog
  entries naming the run. Rejected / application-specific patches are never written.

## 5. Refusal conditions
- Never apply a patch the user has not approved.
- Never edit the Voice Sample.
- Never write application-specific framing (`whd_worthy: false`) into the WHD.
