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

Cap ~3 rounds per type; overflow to a punch list.

## 6. Exit criteria + render
- The loop does not terminate until `tags.py` reports **clean** (zero blocking
  tags) AND the voice audit passes AND the length round (§5) is resolved —
  `length_budget.py` reports **fits** at 2 pages, OR the user recorded an override
  reason in `length_override.md`. Length is a *default*, not a hard block: unlike
  the tags gate, a justified override lets the render proceed past 2 pages.
- If the user stalls, save with an explicit **NOT SUBMITTABLE** banner and the
  list of what remains — never render a tagged draft as final.
- On clean: strip informational tags, write `resume_final.md` (source of truth),
  then render: `python skill/helpers/render_docx.py <run>/resume_final.md
  <run>/resume_final.docx` (ATS-safe: single column, standard font, no
  tables/text-boxes/headers). Deliverables: `resume_final.docx` + `resume_final.md`.

## 7. Refusal conditions
- No fabrication. Every added claim traces to the resume or a cited WHD anchor.
- Never render while blocking tags remain.
- The report carries the standing reminder: read the final draft aloud before submitting.
