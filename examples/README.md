# examples — synthetic end-to-end fixture

Everything here is **synthetic**. "Alex Rivera" is not a real person; "Acme
Robotics" is not a real company. No personal data lives in this repo — this
fixture is what the Python helpers and (later) the integration tests run
against, so real candidate data is never needed to develop the skill.

- `synthetic-whd.md` — a fake candidate's Work History Document, in the same
  restructured format as a real WHD (front-matter role index, `<!-- anchor: -->`
  markers, canary token).
- `acme-robotics-senior-pm/` — one run's worth of artifacts:
  - `jd.txt` — the raw job description (skill input)
  - `resume.md` — the candidate's current resume (skill input)
  - `requirements.yaml` — the JD parsed once (Phase A)
  - `scd.yaml` — research subagent output (Phase B)
  - `gapmap.yaml` — fit subagent output (Phase B)
  - `screen.yaml` — screening subagent output (Phase D)
  - `prescriptions.yaml` — synthesis prescriptions (Phase E)
  - `report.md` — the unified verdict report (Phase E)
  - `appendix.md` — auditable score math, full Gap Map, screening reasoning (Phase E)

The scenario: a SaaS + IoT product manager applying to a robotics platform role.
A realistic "apply with edits" case — strong on platform strategy and
hardware-to-production, with honest gaps in robotics domain depth and ROS.
