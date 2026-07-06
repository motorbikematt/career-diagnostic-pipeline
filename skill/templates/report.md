<!--
report.md TEMPLATE (plan section 3). Verdict-first, 1-2 pages, ~600-900 words.
Fill the placeholders; keep the section order. Everything auditable but not
headline-worthy (score math, full Gap Map, persona reasoning, competitive
comparison) goes in appendix.md, never here.
Numbers strip: paste from `numbers_strip.py <run>` — do not hand-transcribe.
The two triggers: quote VERBATIM from screen.yaml.
-->

# {{Company}} — {{Role}}

**{{Apply | Apply with edits | Do not pursue}} — {{Worth-It tier}} ROI, {{Scope of Work}}.**
<!-- One sentence: the decision, the ROI tier, and the scope of edits together. -->

## Numbers
- Paper score: **{{paper_score}}/100**
- Recoverable gaps: **{{recoverable_gaps_count}}**
- Escalation likelihood: **{{strong | competitive | fragile | unfavorable}}**
- Evidence confidence: **{{high | medium | low | default}}**

## The two triggers
- **First friction:** {{first_friction_trigger — verbatim from screen.yaml}}
- **First escalation:** {{first_escalation_trigger — verbatim from screen.yaml}}

## Prescriptions
<!-- Rendered from prescriptions.yaml. Every Recoverable Gap MUST have an Add row
     citing a WHD section (enforced by prescriptions.py). -->

| Edit | Why | Source (WHD) |
|---|---|---|
| {{Reframe/Add/Remove/Reorder: target}} | {{what it signals now → what it needs to signal; what it closes}} | {{role-N.project-M or —}} |

## Honesty
You can honestly present as: **{{genuine positioning}}**.
You cannot claim: **{{hard-no items}}**.
<!-- Two sentences, no elaboration. Flag any load-bearing stretch here. -->

## Shadow requirements
<!-- From scd.yaml — only those NOT already covered by a prescription row. -->
- {{shadow requirement}}

## Open questions
<!-- Information gaps blocking editing, if any. Omit the section if none. -->
- {{information gap to resolve before editing}}

---
*Before submitting, read the final resume aloud — the finishing loop reduces
AI-voice drift but does not eliminate it.*
