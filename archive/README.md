# archive

Superseded artifacts, retained for history. Not part of the active skill.

- `career-pipeline-orchestrator.jsx` — the v1 browser-side orchestrator. Deprecated: it used abbreviated (non-FINAL) stage prompts, a hardcoded model, and client-side API calls. Replaced by the v2 `/resume-fit` skill.
- `Pipeline_Users_Guide_v1.md` — the v1 user guide, describing the six manual copy-paste prompt stages (Career Documentarian, SCD Generator, Resume Micro Fit Check, Macro Hiring Assessment, Resume Optimization Triage, Ghost-Editor) and their own Gate 1/Gate 2 heuristics. Superseded by the v2 `/resume-fit` skill's Phase A–H structure — see `docs/Pipeline_Users_Guide_v2.md`. The v1 and v2 Gate numbers name unrelated concepts; do not cross-reference them.
- `Pipeline-System-Summary.md` — the v1 architecture summary describing the prompt-file system and its JSX orchestrator wrapper. Superseded by `.claude/skills/resume-fit/SKILL.md`.
- `prompts/` — the v1 six-stage prompt files (career-documentarian, intelligence-analyst, resume-auditor, recruiter-simulation, optimization-strategist, ghost-editor), meant to be pasted manually into Claude conversations in sequence. Superseded by the v2 `/resume-fit` skill's subagent contracts (`.claude/skills/resume-fit/contracts/`), which port these prompts' invariants verbatim — see the citation at the top of each contract file for the v1→v2 mapping.
- `TODO_v1.md` — the v1 TODO list, entirely superseded items (v1 orchestrator work, Work History Builder) already checked off at the time of archiving. The live backlog is the repo root `TODO.md`.

See `MIGRATION_NOTES.md` for the full history of what moved here and when.
