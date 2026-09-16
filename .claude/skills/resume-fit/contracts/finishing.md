# Finishing (Ghost Editor + interactive loop)

Ported from `prompts/ghost-editor` (v1 Stage 4 Draft). **Model:** strong
(Opus-class). v2 INVERTS the deliverable: the tagged draft is generated but
**never shown as the deliverable** — it becomes the finishing loop's worklist.
The system interviews the user until zero blocking tags remain, then renders.

## 1. Role
Ghost Editor: produce a job-targeted resume draft that preserves the candidate's
voice, applying ONLY the synthesis prescriptions.

## 2. Invariants (verbatim from the v1 FINAL prompt — DO NOT PARAPHRASE)
- **Voice source:** the Candidate Voice Sample section of the WHD (anchor
  `voice-sample`) is the primary voice source; the current resume's bullets are
  the secondary source (formatting conventions). "Lock the combined analysis as
  the Voice Profile. All new or reframed content must conform. If a rewrite
  sounds noticeably different from the Voice Sample's natural style, it fails."
- "Preserve original language wherever [the] Prescriptions did not flag a change.
  Do not improve, polish, or rephrase unflagged content."
- "Reframe only what [the] Prescriptions specified. Each edit must trace to a
  specific Reframe, Add, Remove, or Reorder item."
- "For Add prescriptions: pull source material from the Work History section
  cited... Rewrite in the candidate's voice... Do not invent details beyond what
  the Work History contains."
- "Do not insert keywords unnaturally. If a missing keyword cannot be integrated
  without sounding forced, flag as 'NOT INTEGRATED -- requires candidate input.'"
- "Respect [the] Honesty Check. Never claim what was classified as Stretch or
  Hard No. If a prescription requires content the candidate cannot honestly
  claim, output '[CANDIDATE TO SUPPLY: description of what is needed and why]'."
- "Do not add a summary/objective section unless one already exists on the
  current resume."
- **Voice Integrity Check:** compare each [CHANGED] line against the Voice Sample
  and unchanged lines; flag hard conformance as "VOICE NOTE: ...".

## 3. Input manifest
The WHD (voice sample + cited sections), the current resume, `prescriptions.yaml`,
`gapmap.yaml` (honesty: which items are Stretch/Hard No), `scd.yaml`.

## 4. Silent draft (worklist, never the deliverable)
Generate the resume as clean markdown with inline tags:
`[CHANGED]`, `[REMOVED]`, `[CANDIDATE TO SUPPLY: ...]`, `[NOT INTEGRATED]`, and
`VOICE NOTE: ...`. Save as `resume_draft.md` in the run folder. Do NOT present it
as the deliverable. **Target 2 pages** (the 2026 default for a senior IC); apply
any Compress/Cut prescriptions from synthesis as you draft. The draft may still
overflow — the length round (§5) resolves it with the user; never pre-truncate
silently to hit the budget.

## 5. The finishing loop (plan section 4)
Interview the user until the draft is clean, highest-stakes first, via
AskUserQuestion, batched by tag type:
- **Supply rounds** — each `[CANDIDATE TO SUPPLY]`: what's needed and why, one
  question. Insert the user's own words near-verbatim (light tense/format
  conformance only) — this sidesteps most voice drift.
- **Keyword rounds** — each `[NOT INTEGRATED]`: offer 2-3 candidate-voice
  integration options plus "skip — leave it out."
- **Voice rounds** — each `VOICE NOTE` / low-confidence `[CHANGED]`: show original
  vs. rewrite; user picks or dictates a third phrasing.
- **Stretch confrontations** — any prescription touching a Stage-3 stretch: the
  user explicitly accepts the honest framing or drops the line. No silent softening.
- **Length round** — run `length_budget.py <draft.md> --max-pages 2` (margin 0.6).
  If it reports **over budget**, present the overflow to the user with BOTH
  signals side by side, then let them decide — never auto-cut:
  - **Cost** — the per-section `height_in` / `rendered_lines` from the helper
    (which section is eating the pages). The helper is value-blind; it only meters
    inches and never recommends what to cut.
  - **Value** — JD-linkage per section from `gapmap.yaml`/`screen.yaml`: which
    content is JD-relevant and recruiter-weighted (protect) vs. tangential (cheap
    to cut). Recent in-demand-domain work is protected even when it's the largest
    section — size is a cost signal, not a cut signal.
  Recommend cutting the *cheap, low-value inches first* (oldest unlinked roles,
  tail sections, redundant summary paragraph) via `AskUserQuestion`, but the user
  makes every call — recency-vs-tenure-gap tradeoffs are theirs. **Override:** if
  the user chooses to exceed 2 pages, capture their stated reason and write it to
  the run as `length_override.md` (reason + final page estimate). Re-run the
  helper after edits until it reports fits OR an override reason is recorded.
  - **Compression candidates (before cutting content):** run
    `python skill/helpers/compress_candidates.py <draft.md>`. It finds claim lines
    with a 3+ item comma/and-separated list mechanically (pattern only — no
    semantic understanding of the items). For each candidate, the MODEL proposes
    an accurate count + category phrase (e.g. "China, Australia, and
    US/Europe/Korea" → "3 trans-continental"; "Aerospace, Automotive, and Toys"
    → "3 verticals") and the user ratifies — a wrong or vague category word is
    worse than the line it would have saved, so this is never auto-applied. Prefer
    compression candidates over cutting content: compressing a true list preserves
    the full claim; cutting a role/bullet loses signal outright.

Cap ~3 rounds per type; overflow to a punch list.

## 6. Exit criteria + render
- The loop does not terminate until `tags.py` reports **clean** (zero blocking
  tags) AND the voice audit passes AND the length round (§5) is resolved —
  `length_budget.py` reports **fits** at 2 pages, OR the user recorded an override
  reason in `length_override.md`. Length is a *default*, not a hard block: unlike
  the tags gate, a justified override lets the render proceed past 2 pages.
- If the user stalls, save with an explicit **NOT SUBMITTABLE** banner and the
  list of what remains — never render a tagged draft as final.

## 6b. Closed-loop re-eval (ONE pass, before promoting the draft to a candidate)
Before writing `resume_candidate.md` (§6), run the clean tagged draft back through
the **same axes the seed resume was judged on** — the tailoring must not have
degraded them. This is exactly ONE pass; it reports, it does not auto-edit or
re-enter any loop.

1. **ATS** — `python skill/helpers/ats.py <requirements.yaml> <resume_draft.md>`.
   Assert keyword coverage did not regress below the seed resume's coverage.
2. **JD-relevance** — `python skill/helpers/relevance.py <resume_draft.md>
   <requirements.yaml> <gapmap.yaml>`. Assert no NEW `none`-linkage claim was
   introduced by the edits, and every retained `none` claim is one the user already
   ratified as a differentiator (§5c) or is structural (contact/education).
3. **Voice** — confirm the §2 Voice Integrity Check passed on the final text.
4. **ATS-unsafe characters** — `python skill/helpers/ats_chars.py <resume_draft.md>`.
   Fixed, JD-independent rule (not a style preference): em/en dashes, curly
   quotes, decorative bullets/arrows, and emoji are documented ATS parsing failure
   points. Must report **clean** before render — this is deterministic, so unlike
   the other three axes there is no "regression tolerance," only clean or not.
   Fixing a violation may require rephrasing (e.g. an em-dash clause becomes two
   sentences) — that judgment belongs to the model/user, not an auto-replace.

Write a short `reeval.md` to the run folder: the axis verdicts + any
regression. **No recursion** — if it flags a regression, surface it to the user as a
single yes/no ("keep as-is or make this one fix?"), never as a new trim cycle. If
clean, proceed to render. If the draft already passed cleanly (no dead-weight, fits
2 pages) this step is a quick confirmation, not an interrogation.

- On clean (tags clean + length resolved + re-eval clean): strip informational
  tags, write `resume_candidate.md` (source of truth), then render:
  `python skill/helpers/render_docx.py <run>/resume_candidate.md <run>/resume_candidate.docx`
  (ATS-safe: single column, standard font, no tables/text-boxes/headers).
  Deliverables: `resume_candidate.docx` + `resume_candidate.md` + `reeval.md`.
  **This is NOT "final."** It has passed every automated gate but still needs the
  user's own read-aloud pass and explicit sign-off (§7). "Final" is reserved for
  the artifact the user actually approves to submit — using it earlier is exactly
  the ambiguity that caused confusion in practice: multiple pipeline runs each
  wrote a file called "final" before the user had actually finished editing.

## 7. Sign-off and final naming (only after the user approves)
- The candidate is never auto-promoted to "final." The user reads it aloud and
  explicitly approves it as ready to submit.
- **The input resume is never renamed.** Whatever file the user provided (any
  name, any location their config points to) stays as-is — the pipeline reads it,
  never rewrites or renames the source.
- On approval, render the true final deliverable using a stable, professional
  naming convention independent of internal revision scratch files:
  `<LASTNAME>_<FIRSTNAME>_<COMPANY>_<DATE>.docx` (e.g.
  `Reyes_Matthew_Anthropic_2026-07-06.docx`), built from the approved
  `resume_candidate.md`. This is the one file named without a pipeline-internal
  suffix — it is meant to be handed to a human, not read by another pipeline step.

## 8. Refusal conditions
- No fabrication. Every added claim traces to the resume or a cited WHD anchor.
- Never render while blocking tags remain.
- The report carries the standing reminder: read the final draft aloud before submitting.
