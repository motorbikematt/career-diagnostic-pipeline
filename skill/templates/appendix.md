<!--
appendix.md TEMPLATE (plan section 3). Everything auditable but not headline:
score math, full Gap Map, persona/screening reasoning, competitive comparison.
Lives in the run folder; never rendered in report.md. "The score derives from
the map" — the map is here and inspectable; it just isn't the headline.
-->

# Appendix — {{Company}} / {{Role}}

## Score math
<!-- Paste from `score.py <gapmap.yaml>`. Python computed this; do not redo it. -->
- Paper score: {{paper_score}}/100  (hard {{hard_score}}, preferred {{preferred_score}})
- Classifications: match {{n}}, partial {{n}}, none {{n}}
- Recoverable gaps: {{ids}}
- Unrecoverable hard gaps: {{ids}}

## Gap Map (full)
<!-- One row per requirement from gapmap.yaml. -->

| ID | Requirement | Type | Weight | Status | Resume evidence | WHD evidence | Recoverable |
|---|---|---|---|---|---|---|---|
| {{hr-1}} | {{text}} | {{hard}} | {{w}} | {{match/partial/none}} | {{...}} | {{...}} | {{yes/no}} |

## Archetypes
- Seeker archetype: {{from gapmap}}
- JD archetype: {{from gapmap}}

## Screening reasoning (WHD-blind)
- Recruiter persona: {{recruiter_persona}}
- Gate 1 (6-second) verdict: {{gate1_verdict}}
- Elimination logic: {{elimination_logic}}
- Hiring-manager acceptance risk: {{hm_acceptance_risk}}

## ATS keyword scan
<!-- From `ats.py <requirements.yaml> <resume>`. -->
- Present: {{...}}
- Missing: {{...}}  (coverage {{n}}%)

## Employer context (SCD)
- Business cycle: {{business_cycle}}  (evidence confidence: {{...}})
- Buyer anxiety: {{...}}
- Sources: {{...}}

## Competitive archetype comparison
- Structural win: {{where the candidate outperforms the standard-path applicant}}
- Structural loss: {{where the candidate is structurally disadvantaged}}
- Ambiguity gap: {{what requires manual verification/translation}}
