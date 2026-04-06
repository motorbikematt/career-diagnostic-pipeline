# Career Diagnostic Pipeline

A multi-stage AI pipeline that finds experience you already have but haven't put on your resume — and tells you whether applying is worth your time before you spend hours tailoring.

Built by [Matthew F Reyes](https://linkedin.com/in/motorbikematt) while navigating his own job search.

---

## The Problem This Solves

Most qualified candidates don't fail to get callbacks because they lack experience. They fail because their resume triggers elimination patterns in a screening process they never see — and because they've forgotten, undersold, or never surfaced work they actually did.

This pipeline addresses both problems before you apply.

---

## What It Does

You paste in your work history, your current resume, and a job description. The pipeline runs six diagnostic stages:

1. **Career Documentarian** — Builds a comprehensive private work history that serves as the source of truth for everything downstream. This is the document you never send to employers.

2. **Intelligence Analyst** — Researches the target employer and produces a strategic brief: what business cycle they're in, what the hiring manager is actually afraid of, and what kind of hire they really need right now.

3. **Resume Auditor** — Maps every JD requirement against your resume and your work history. Finds recoverable gaps — experience you have but haven't surfaced — and scores your fit on transparent weighted math.

4. **Recruiter Simulation** — Stress-tests your resume against a modeled screening process. Identifies exactly where a recruiter loses interest and where something compels them to call.

5. **Optimization Strategist** — Synthesizes everything into a specific action plan: what to reframe, what to add, what to remove, and what you can honestly claim versus what you cannot.

6. **Ghost Editor** *(optional)* — Produces a voice-calibrated resume draft under time pressure. Tagged so you can see every change. Treat as a draft, not a submission.

---

## What It Will Not Do

- Tell you that you are a great fit when you are not
- Invent experience you do not have
- Guarantee a callback
- Replace your judgment about whether a role is right for you

---

## How to Use It

### Claude Pro subscribers
Use the orchestrator in `ui/career-pipeline-orchestrator.jsx` — paste it into a Claude Artifact and run the full pipeline in one session with streaming output per stage.

### Claude Free tier
Run each stage manually by pasting the prompt files from `prompts/` into Claude in sequence. Each stage directory contains the prompt, a handoff template showing what to carry forward, and an example output so you know what to expect.

---

## Repo Structure

```
career-diagnostic-pipeline/
├── prompts/
│   ├── career-documentarian/     ← Start here. Build this once, maintain it.
│   ├── intelligence-analyst/     ← Run per application with employer sources
│   ├── resume-auditor/           ← Run per application (parallel with above)
│   ├── recruiter-simulation/     ← Requires resume-auditor output
│   ├── optimization-strategist/  ← Convergence stage, requires all prior outputs
│   └── ghost-editor/             ← Optional. Use only under time pressure.
├── ui/
│   └── career-pipeline-orchestrator.jsx
└── docs/
    ├── pipeline-system-summary.md
    └── pipeline-users-guide.md
```

---

## Where to Start

Read `docs/pipeline-users-guide.md` first. Then build your Career Documentarian file before running any other stage — every downstream stage depends on it.

---

## Model Requirements

| Stage | Recommended Model |
|---|---|
| Career Documentarian | Claude Sonnet |
| Intelligence Analyst | Claude Sonnet |
| Resume Auditor | Claude Sonnet |
| Recruiter Simulation | Claude Opus |
| Optimization Strategist | Claude Opus |
| Ghost Editor | Claude Opus |

---

## License

MIT — use freely, attribution appreciated.

---

## Contributing

This is a v1.0 community release. Issues and PRs welcome. See `TODO.md` for known gaps and planned improvements.