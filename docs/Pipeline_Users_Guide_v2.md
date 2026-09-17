# Resume Fit Pipeline — User Guide (v2)

## 1. Purpose

This is a diagnostic pipeline for evaluating your fit against a specific job
before you apply. It does not write your resume from scratch. It tells you
whether to apply, what will get you screened out, what to change if you
proceed, and where in your work history to find the material for those
changes — then, if you want it, produces a submission-ready resume.

The pipeline exists because the most common reason qualified candidates fail
to get callbacks is not lack of qualification — it is that their resume
triggers elimination patterns in a screening process they never see, or that
they've forgotten, undersold, or never surfaced work they actually did. This
pipeline addresses both problems before you submit anything.

v2 is a full rebuild of the original six-stage, copy-paste-between-prompts
system. It is now a single Claude Code skill (`/resume-fit`) that orchestrates
subagents and deterministic Python helpers directly — no manual handoffs
between prompt files. The old system is archived at
[`../archive/Pipeline_Users_Guide_v1.md`](../archive/Pipeline_Users_Guide_v1.md);
its Gate 1/Gate 2 terminology names different concepts than v2's and the two
should not be cross-referenced.

## 2. Outcome

After running the pipeline against a job description, you will have:

- A verified understanding of the employer's strategic context and what kind
  of hire they actually need.
- A line-by-line map of where your experience matches the job's requirements,
  where it partially matches, and where it is genuinely absent.
- A numerical fit score anchored to transparent, inspectable math — never the
  deciding factor on its own.
- A heuristic stress test of how a recruiter would screen your resume without
  ever seeing your full work history.
- A clear verdict: Apply, Apply with edits, or Do not pursue.
- If you proceed: a specific, WHD-sourced prescriptions list, and — after you
  approve moving forward — a tailored, ATS-safe `.docx`.

You will not get a resume assembled unattended. Every non-mechanical judgment
call is surfaced to you as a question, and nothing gets fabricated to close a
gap.

## 3. The two-plane model

- **Code plane** — this repository. Skill logic, helper scripts, schemas,
  templates, and a synthetic example fixture. User-agnostic; contains no
  personal data, ever.
- **Data plane** — a private folder you configure, separate from this repo
  (e.g. `career-diagnostic-pipeline-data`, kept as a sibling directory, not
  nested inside this repo and not tracked in git). Holds your Work History
  Document (WHD) and every run folder the pipeline creates.

On first use, if no data plane is configured, the skill asks where yours lives
and persists that path via:

```bash
python .claude/skills/resume-fit/helpers/config.py set "/path/to/your/data-plane"
```

Resolution order: the `$RESUME_FIT_DATA_PLANE` environment variable, then
`~/.config/resume-fit/config.yaml`. Your data plane must contain
`pipeline/whd/<your WHD>.md`.

## 4. Three properties that are never compromised

1. **Honesty guardrails.** Every claim on your resume is classified — genuine,
   stretch, or hard no — and nothing gets fabricated to fill a gap.
2. **Screening blindness.** The screening step sees only what a recruiter
   would see. It never has access to your WHD. This is enforced structurally
   (the WHD is never in its input, it has no file-read tools, and a canary
   token would fail the run if a leak occurred) — not by asking it nicely.
3. **Conservative default.** When employer evidence is thin, the pipeline
   assumes a skeptical, risk-averse screener rather than a receptive one.

## 5. The phases

Each phase after A dispatches on the model that fits its job: cheap/fast for
research and fit extraction, the strong model for screening and synthesis
(the parts of the pipeline where reasoning quality matters most).

**Phase A — Intake.** Confirms the JD, your current resume, and your WHD are
all located. Parses the JD once into `requirements.yaml` — every later phase
reads this structured form, never the raw JD text. Creates a per-run folder
under your data plane.

**Phase B — Parallel research + fit.** Two subagents run concurrently, each
seeing only what it needs: a research subagent produces a Strategic Context
Document (`scd.yaml`) — the employer's business cycle, likely hiring anxiety,
and shadow requirements the JD doesn't state outright. A fit subagent compares
your resume and WHD against the JD's requirements (`gapmap.yaml`), without
ever seeing the research findings. If either surfaces something fundamental —
an archetype mismatch, or research that changes whether you'd even want this
job — you're asked about it here, before more expensive phases run on a
premise that's already wrong.

**Phase C — Gate 1 (Gap Brief).** A zero-token Python step tallies
unrecoverable gaps against categorical trip rules — never a raw score cutoff.
If it trips, you get one structured question with exactly three answers:
**Stop** (archive and end the run), **Proceed anyway** (gaps get recorded in
the report's Open Questions, not hidden), or **Contest a gap** (you have real
evidence — this routes into a short interview, patches your WHD, and
recomputes the tally before continuing).

**Phase D — Screening.** A strong-model subagent simulates how a recruiter
would actually process your resume, using only what a recruiter would have:
your resume, the parsed requirements, a screening-safe gap summary, and the
research brief — never your WHD. A deterministic canary scan afterward
verifies no WHD content leaked into its output. Produces `screen.yaml`.

**Phase E — Synthesis.** The convergence step. Reads everything, including
your WHD, and produces `report.md` (the verdict-first, ~600–900 word report
you actually read) plus `appendix.md` (the auditable score math, full gap map,
and screening reasoning, for when you want to check the work). Every
recoverable gap in your favor must have a prescription backed by a real WHD
source — enforced mechanically, not just asserted. Also runs a JD-relevance
pass that flags resume claims with zero connection to this specific job; you
decide what's dead weight versus a deliberate differentiator, nothing gets cut
automatically.

**Phase F — Gate 2.** You read the report, then choose: proceed to drafting,
stop here, or resolve open information gaps first (which can loop back into
WHD reconciliation before synthesis re-runs on the affected sections).

**Phase G — Finishing loop.** Only runs after you choose to proceed. Produces
a tagged working draft applying only the approved prescriptions, then walks
you through batched questions (missing detail, keyword phrasing, voice,
stretch claims, and length) until the draft is clean. A length round shows you
per-section cost against per-section JD-relevance so any cuts are your call,
never automatic. A closed-loop re-check (ATS keywords, relevance, forbidden
characters) confirms the finished draft didn't regress versus the seed before
it's rendered to an ATS-safe `.docx`. You read the final result yourself and
explicitly approve it before it's treated as truly final.

**Phase H — WHD reconciliation.** Every run surfaces new facts, corrections,
or evidence uncovered along the way. Each is classified as durable
(WHD-worthy) or run-specific; only durable ones become a proposed patch, shown
to you as a diff, and applied only once you approve it. This is how your WHD
gets more complete and accurate over time as a side effect of using the
pipeline — never edited silently, and your Voice Sample is never touched.

## 6. What it will not do

- Tell you you're a great fit when you're not.
- Invent experience you don't have.
- Let a screening subagent see your full work history.
- Auto-cut or auto-rewrite your resume without asking you first.
- Guarantee a callback, or replace your own judgment about whether a role is
  right for you.

## 7. How to use it

This is a Claude Code skill, not a set of prompts to paste manually. From a
Claude Code session rooted at (or under) this project, invoke:

```
/resume-fit
```

and supply a JD — a file path, pasted text, or a URL. The skill handles
first-run data-plane setup, then walks the phases above, pausing for your
input exactly where this guide says it will.

## 8. Deterministic helpers

The arithmetic, string-matching, and mechanical checks are never done by the
model — they're plain, unit-tested Python, invoked as CLI scripts. See the
full table in
[`.claude/skills/resume-fit/SKILL.md`](../.claude/skills/resume-fit/SKILL.md#deterministic-helpers-never-spend-a-token)
for the complete list (schema validation, the Gate 1 tally, ATS keyword
scanning, the relevance meter, length budgeting, the docx renderer, and more).

## 9. Where to go next

- [`.claude/skills/resume-fit/SKILL.md`](../.claude/skills/resume-fit/SKILL.md)
  is the canonical, most detailed spec this guide summarizes — read it if
  you're extending the skill rather than just using it.
- [`.claude/skills/resume-fit/contracts/`](../.claude/skills/resume-fit/contracts)
  holds the full behavioral contract for each subagent phase.
- [`examples/`](../examples) has a complete synthetic end-to-end run (fake
  candidate, fake company) showing every artifact the pipeline produces.
- [`../TODO.md`](../TODO.md) tracks what's still open, including the
  public-release backlog for first-time users with no existing WHD.
