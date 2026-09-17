# Career Diagnostic Pipeline

A Claude Code skill that finds experience you already have but haven't put on
your resume — and tells you whether applying is worth your time before you
spend hours tailoring.

Built by [Matthew F Reyes](https://linkedin.com/in/motorbikematt) while
navigating his own job search.

---

## The Problem This Solves

Most qualified candidates don't fail to get callbacks because they lack
experience. They fail because their resume triggers elimination patterns in a
screening process they never see — and because they've forgotten, undersold,
or never surfaced work they actually did.

This pipeline addresses both problems before you apply.

---

## What It Does

Point the skill at a job description and it runs eight phases end to end:
parses the JD, researches the employer, maps your fit against your resume and
private work history, simulates how a recruiter would actually screen you,
synthesizes a verdict report, and — only once you say go — drafts an ATS-safe
resume and folds anything durable it learned back into your work history for
next time.

- **Phases A–D (diagnostic)** — intake, employer research + fit mapping run in
  parallel, a Gap Brief gate on unrecoverable gaps, and a recruiter-screening
  simulation that never sees your full work history.
- **Phase E (synthesis)** — one concise report: Apply / Apply with edits / Do
  not pursue, with the reasoning and the score math both shown, never just the
  score.
- **Phases F–H (only if you proceed)** — a finishing loop that drafts a
  tailored resume with you approving every non-mechanical change, and a
  reconciliation step that improves your standing work history document as a
  side effect of the run.

Full phase-by-phase detail: [`docs/Pipeline_Users_Guide_v2.md`](docs/Pipeline_Users_Guide_v2.md).

---

## What It Will Not Do

- Tell you that you are a great fit when you are not
- Invent experience you do not have
- Let the screening step see your full work history
- Auto-cut or auto-rewrite your resume without asking first
- Guarantee a callback, or replace your own judgment about a role

---

## How to Use It

This runs as a Claude Code skill, not a set of prompts you paste by hand.

1. Clone this repo, and from a Claude Code session rooted at (or under) it,
   invoke:
   ```
   /resume-fit
   ```
2. On first run, you'll be asked where your **data plane** lives — a private
   folder, kept outside this repo, holding your Work History Document (WHD)
   and every run's artifacts. This repo never contains your personal data.
3. Supply a job description (file path, pasted text, or URL) and follow the
   pipeline through the phases above. It pauses for your input exactly where
   a judgment call — not a mechanical check — needs to be made.

---

## Repo Structure

```
career-diagnostic-pipeline/
├── .claude/skills/resume-fit/   ← the skill: SKILL.md, subagent contracts,
│                                   deterministic helpers, schemas, templates
├── docs/
│   └── Pipeline_Users_Guide_v2.md   ← start here for the full walkthrough
├── examples/                    ← a complete synthetic end-to-end run
├── tests/                       ← pytest suite for the deterministic helpers
├── archive/                     ← superseded v1 prompt-orchestrator + docs
└── TODO.md                      ← open work, including the public-release backlog
```

---

## Two-Plane Model

- **Code plane** (this repo) — skill logic, helpers, schemas, templates, and a
  synthetic example fixture. User-agnostic. No personal data, ever.
- **Data plane** (private, yours) — your WHD and per-run folders, located via
  configuration and never hardcoded. See
  [`docs/Pipeline_Users_Guide_v2.md`](docs/Pipeline_Users_Guide_v2.md#3-the-two-plane-model).

---

## Model Requirements

The skill routes models per phase rather than requiring you to pick one:
cheap/fast for research and fit extraction, a strong model for screening
simulation and synthesis, where reasoning quality matters most.

---

## License

MIT — use freely, attribution appreciated.

---

## Contributing

This is the v2 rebuild, in active use. Issues and PRs welcome. See
[`TODO.md`](TODO.md) for known gaps and planned improvements, including the
onboarding mode still needed for a first-time user with no existing WHD.

---

## History

v1 was a six-prompt, copy-paste-between-Claude-conversations system. It's
archived at [`archive/`](archive) — see `archive/README.md` for what changed
and why.
