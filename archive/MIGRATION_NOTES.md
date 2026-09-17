# Migration notes

What this archive holds, why it exists, and exactly what moved here and when.
This file is scoped to the archive only — for the project's broader session
history and decision rationale, see `local/context/journal/project_journal.md`
(not part of the public repo).

## What v1 was

The pipeline launched 2026-04-05 as a set of six prompt files meant to be
pasted manually, in sequence, into separate Claude conversations: a one-time
Career Documentarian interview to build a private work history document, then
per-application Intelligence Analyst (Stage 0) → Resume Auditor (Stage 1) →
Recruiter Simulation (Stage 2) → Optimization Strategist (Stage 3) → an
optional Ghost-Editor (Stage 4). A JSX file (`career-pipeline-orchestrator.jsx`)
offered a lighter-weight way to run all six in one Claude Artifact session for
Pro subscribers.

## What triggered the rebuild and this cleanup

Starting 2026-07-06, the pipeline was rebuilt (Phases 1–6, completing the same
day) as a single Claude Code skill — `.claude/skills/resume-fit/` — replacing
manual copy-paste with subagent dispatch, deterministic Python helpers, and
schema-validated artifacts. The v1 prompts' load-bearing invariants (honesty
guardrails, screening blindness, conservative defaults) were ported verbatim
into the v2 subagent contracts rather than rewritten from scratch; each
contract file cites its v1 source at the top.

The rebuild didn't retire the old material at the time. By 2026-09-16, three
separate copies of "what this pipeline is" had drifted out of sync with the
actual v2 architecture: `README.md` and `docs/` still described the v1
six-stage system as current, the skill itself was sitting at a repo-root
`skill/` directory Claude Code doesn't scan (rather than `.claude/skills/`,
where it's discoverable), and the `prompts/` directory sat at repo root
alongside `.claude/`, `docs/`, and `examples/` — with the same apparent
standing as those active directories, despite containing operational
instructions ("Run Stage 0 with the JD...") for a system no longer in use.
This is the same failure mode each time: stale material left where it reads as
current, rather than clearly marked as historical.

## Inventory: what moved here, and when

| Item | Moved | Replaced by |
|---|---|---|
| `career-pipeline-orchestrator.jsx` | before 2026-09-16 (prior session) | `.claude/skills/resume-fit/` (the skill itself) |
| `Pipeline_Users_Guide_v1.md` (from `docs/`) | 2026-09-16 | `docs/Pipeline_Users_Guide_v2.md` |
| `Pipeline-System-Summary.md` (from `docs/`) | 2026-09-16 | `.claude/skills/resume-fit/SKILL.md` |
| `prompts/` (6 stage files, from repo root) | 2026-09-16 | `.claude/skills/resume-fit/contracts/` |
| `TODO_v1.md` (was `TODO.md`'s superseded sections) | 2026-09-16 | root `TODO.md`, now v2-only |

All moves used `git mv`, so file history is preserved — `git log --follow` on
any file here traces back through its pre-archive path.

## For a reader landing here cold

Nothing in this directory is wired into the active skill at runtime. The
citation lines in `.claude/skills/resume-fit/contracts/*.md` ("Ported from
`archive/prompts/...`") are historical attribution, not live dependencies —
the skill runs entirely without this directory present. If you're evaluating
or extending the pipeline, start at the repo root `README.md`, then
`docs/Pipeline_Users_Guide_v2.md`, then `.claude/skills/resume-fit/SKILL.md`.
