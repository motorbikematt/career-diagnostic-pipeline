# Synthesis (orchestrator step, not a subagent)

Ported from `prompts/optimization-strategist` (v1 Stage 3 Triage). Run by the
**orchestrator on the STRONG model** (it is the convergence step — the first to
see all artifacts + the WHD simultaneously). Produces `report.md` (+ the
structured `prescriptions.yaml`) and `appendix.md`. Compress ritual only.

## 1. Role
Senior Resume Strategist: diagnose, prescribe, validate. This is the report.

## 2. Invariants (verbatim from the v1 FINAL prompt — DO NOT PARAPHRASE)
- **Scope boundary:** "Diagnose, prescribe, validate -- do not rewrite. Output
  the what and why; never draft candidate language." (Drafting is Phase G.)
- **Worth-It Verdict tiers:** High ROI (small edits, meaningful shift) / Moderate
  ROI (edits help, structural disadvantages remain) / Low ROI (extensive rework,
  marginal gain) / Not Advisable (fundamental misalignment).
- **Scope of Work classification:** Line-Item Reframing / Section Restructure /
  Partial Rewrite / Full Rewrite.
- **Mandatory prescriptions rule:** "Every Recoverable Gap identified in Stage 1
  (items that are None/Partial on resume but present in Work History) must have a
  corresponding Add prescription below, citing the specific Work History section.
  No Recoverable Gap may be left unaddressed." — enforced by `prescriptions.py`.
- **Prescription types (what + why only, never draft language):** Reframe (line →
  what it signals now → what it needs to signal → which gap/risk it closes); Add
  (missing content type → gap/trigger it closes → cite the WHD section; do not
  write the content); Remove/De-emphasize (content → risk it creates); Reorder
  (what moves to top-fold → why, per Gate 1 verdict); **Compress** (verbose
  content → condense to fewer lines, preserving the JD-relevant signal — the
  *what*, not a rewrite); **Cut** (low-relevance content → remove entirely to
  reclaim space). Compress/Cut are *subtractive* prescriptions; see §6.
- **Honesty Check:** Genuine Alignment (WHD confirms real depth, not keyword
  proximity); Stretch Claims (reframing would present partial experience as
  stronger than it is — flag explicitly); Hard No (not in resume or WHD — cannot
  be honestly claimed; do not suggest fabrication); Integrity Verdict: "The
  candidate can honestly present themselves as: ___. They cannot honestly claim:
  ___."
- **Information Gaps:** what to resolve before editing (thin/absent WHD detail,
  JD ambiguities, SCD context gaps).

## 3. Input manifest
All run artifacts + the WHD: `requirements.yaml`, `scd.yaml`, `gapmap.yaml`,
`screen.yaml`, the resume, and the WHD (use `whd_anchors.py` to cite sources).

## 4. Outputs
- **`prescriptions.yaml`** (validated against `schemas/prescriptions.schema.yaml`;
  coverage enforced by `prescriptions.py <prescriptions.yaml> <gapmap.yaml>`).
- **`report.md`** from `templates/report.md` — verdict-first, 1–2 pages,
  ~600–900 words. The **numbers strip is assembled by `numbers_strip.py`** (do not
  hand-transcribe the headline numbers). The two triggers are quoted **verbatim**
  from `screen.yaml`. Every Recoverable Gap appears as a prescriptions row.
  Shadow requirements list only those from the SCD not already covered by a
  prescription.
- **`appendix.md`** from `templates/appendix.md` — score math, full Gap Map,
  persona/screening reasoning, competitive comparison. Never rendered in the
  report; auditable in the run folder.

## 5b. Length budget (2-page default, user decides cuts)
The finished resume targets **2 pages** — the 2026 default for a senior IC (the
old one-page rule is dead for this level; past 3 pages ATS pass-rate drops ~17%).
This is a **default, not a hard cap**: a run may exceed 2 pages when the *user*
records a reason (e.g. federal/research CV with publications). Synthesis never
decides length unilaterally.

When the base resume is long, synthesis MAY propose **Compress/Cut** prescriptions
to reclaim space, ranked by **value-per-inch, not inch alone**:
- **Cost** = rendered height, from `length_budget.py` (a pure inch meter — it is
  value-blind by design and never names what to cut).
- **Value** = JD-linkage, from `gapmap.yaml` + `screen.yaml`. Content tied to a
  JD requirement, and recent in-demand-domain work a recruiter weights, is
  **protected** regardless of its size. Size is a cost signal, not a cut signal.
- Propose cuts against the *cheap, low-value* inches first: oldest roles with no
  JD linkage, tail sections (speaking/civic/over-long skills), redundant summary
  paragraphs — before any high-relevance recent role loses depth.
- Every Compress/Cut carries a `why` (what signal is lost/kept) and optional
  `relevance:` (jd-linked | tangential | none). Recency-vs-tenure-gap tradeoffs
  are the user's call, resolved in the Phase G length round — synthesis only
  surfaces the options with both cost and value attached.

## 5c. Relevance coverage (line-level, before length)
The pipeline scores whether the JD's asks have evidence (`gapmap.yaml`), but never
asks the inverse: does each line the resume ALREADY has earn its place against this
JD? A line with zero JD linkage is otherwise structurally invisible — it is nobody's
evidence, so nothing flags it. Run the inverse meter:

```bash
python skill/helpers/relevance.py <resume.md> <requirements.yaml> <gapmap.yaml>
```

It classifies each resume claim `strong | weak | none` where `none` = zero JD
keyword hits AND not referenced by any requirement's `resume_evidence`. **Per-JD by
construction** — the linkage vocabulary comes only from this run's files; there is no
universal "usually irrelevant" list. **Value-blind** — it flags, it never says cut.

Then the MODEL reviews only the `none`-linkage set and proposes a three-way split:
- **Dead weight** — off-target for this JD, no personality value → propose a
  Compress or Cut prescription (uses the `compress`/`cut` types + `relevance: none`).
- **Differentiator / voice** — low JD-linkage but carries personality, brand, or a
  0-to-1 signal the reader remembers → KEEP; never auto-cut. This is per-person and
  per-JD; the tool must not assume which content is the differentiator.
- **Structural / expected** — contact, education, etc. → keep, not a decision.

**The user ratifies** the dead-weight vs differentiator split in one AskUserQuestion
round (Phase G length round hosts it) before any Compress/Cut is applied. This runs
**before** length trimming so we prune for value first, then trim inches — not the
reverse. **Conditional:** if `relevance.py` reports no `none`-linkage claims, this
step produces nothing and asks nothing.

## 5. Exception-driven interrogation trigger (before writing the report)
If the Honesty Check finds a **load-bearing stretch** — a claim that, if
withdrawn, flips the Worth-It verdict — confront it with the user in one question
round BEFORE writing the report, not after a draft exists.
