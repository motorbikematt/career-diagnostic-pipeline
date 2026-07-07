# TODO

## Immediate — SUPERSEDED by Resume Pipeline v2
The v1 orchestrator work below is retired. The pipeline is being rebuilt as a
single `/resume-fit` skill (subagents + Python helpers) per the Resume Pipeline
v2 plan. Kept for historical context.
- [x] ~~Sync JSX system prompts to FINAL.md content~~ — v2 ports FINAL prompts into subagent contracts
- [x] ~~Fix model routing in orchestrator~~ — v2 routes models at the orchestrator level
- [x] ~~Rename `motorbike-orchestrator.jsx`~~ — orchestrator moved to `archive/`
- [x] ~~Define canonical handoff output schema per stage~~ — v2 uses validated YAML artifacts
- [x] ~~Generate synthetic example outputs for all six stages~~ — v2 ships one synthetic end-to-end fixture in `examples/`
- [x] ~~Generate handoff templates for IA, RA, RS, OS~~ — replaced by the subagent contract template

## Work History Builder — SUPERSEDED by Resume Pipeline v2
Folded into the v2 WHD restructure (front-matter index, stable anchors,
changelog) and the in-workflow reconciliation loop. Kept for historical context.
- [x] ~~Define canonical output schema~~ — v2 WHD schema (§5 of the v2 plan)
- [x] ~~Enforce schema in career-documentarian.md prompt~~ — becomes the v2 onboarding mode (see v2 public release)
- [x] ~~Create `work-history-template.md`~~ — v2 ships `skill/templates/whd-template.md`
- [x] ~~Restructure existing work history document~~ — v2 Phase 1

## v2 public release
For strangers to install and use the skill without the author's data:
- [ ] Onboarding mode: port the Pre-Stage Career Documentarian interview into the skill (new users have no WHD)
- [ ] README rewrite: describe v2 install and use
- [ ] Strip any incidental personal references from `docs/`
Schedule after Phase 7 validation.

## Post v1.0 (roadmap)
- [ ] Performance review support as Day 1 value proposition
- [ ] Interview preparation module (diary data already structured for this)
- [ ] Outcome tracking 
- [ ] Cover letter generation (trivial Stage 4 extension)
- [ ] Chrome extension / job capture mechanism
- [ ] Application tracking / CRM
- [ ] GitHub Pages if non-technical users struggle with README
- [ ] Validate behavioral hypothesis (Workday Career Profile interviews)
- [ ] CareerLog hands-on evaluation
