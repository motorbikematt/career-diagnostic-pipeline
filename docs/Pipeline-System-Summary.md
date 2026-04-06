# Career Diagnostic Pipeline — System Summary

## What This Is

An AI-powered diagnostic pipeline that evaluates a job seeker's fit against a specific job description before they apply. It does not write resumes. It determines whether to apply, what will trigger elimination, what to change if proceeding, and where in the candidate's documented work history to find the material for those changes.

The pipeline is a set of structured prompt files. Each stage has a defined role, guard clauses that block execution on missing inputs, explicit input requirements, and a structured output format that feeds downstream stages. It runs inside Claude conversations; `career-pipeline-orchestrator.jsx` provides a UI wrapper.

---

## Core Insight

The most common reason qualified candidates fail to get callbacks is not lack of qualification — it is that their resume triggers elimination patterns in a screening process they never see. Recruiters spend seconds on initial review. Hiring managers skim for pattern recognition. Both are looking for reasons to discard, not reasons to engage.

A second insight drives the architecture: **the resume is the pipeline's weakest input.** Most candidates cannot accurately recall what they did, at what scale, or with what outcome under application pressure. The Pre-Stage Work History Builder exists to create a source-of-truth document before narrative shaping occurs — capturing evidence contemporaneously rather than reconstructing it under deadline.

---

## Architecture: Six Stages

| Stage | File | Role | Runs |
|-------|------|------|------|
| Pre-Stage | `prompts/career-documentarian/career-documentarian.md` | Career Documentarian | Once; maintained as living document |
| Stage 0 | `prompts/intelligence-analyst/intelligence-analyst.md` | Strategic Intelligence Analyst | Once per application |
| Stage 1 | `prompts/resume-auditor/resume-auditor.md` | Expert Resume Auditor | Once per application |
| Stage 2 | `prompts/recruiter-simulation/recruiter-simulation.md` | Executive Recruiter / Risk Analyst | Once per application |
| Stage 3 | `prompts/optimization-strategist/optimization-strategist.md` | Senior Resume Strategist | Once per application |
| Stage 4 | `prompts/ghost-editor/ghost-editor.md` | Ghost Editor | Optional |

Each stage has a Guard clause that halts execution and outputs a single error line if required inputs are absent. Skipping stages degrades output quality in specific, documented ways — Stage 2 without Stage 1's Handoff Variables cannot produce a calibrated elimination risk assessment; Stage 3 without Stage 2 cannot distinguish paper gaps from perception gaps.

Recommended models: Sonnet for Pre-Stage, Stage 0, and Stage 1. Opus for Stage 2, Stage 3, and Stage 4.

---

## Stage Descriptions

### Pre-Stage: Career Documentarian

The Pre-Stage is an interactive interview session, not a single-pass prompt. It produces the Work History Document — a private, structured record of the candidate's full professional history that serves as the source of truth for all downstream stages. This document is never sent to employers.

**Why this stage exists as a discrete unit:** The resume and the Work History Document are different objects serving different purposes. The resume is a curated marketing artifact shaped by what the candidate thought was relevant at the time they last updated it. The Work History Document is an exhaustive record captured without regard to any specific application. This separation enables the pipeline's most differentiated capability: identifying *recoverable gaps* — requirements the candidate meets based on their actual experience but has not surfaced on their resume. Without the Pre-Stage, the pipeline can only evaluate what is already on paper.

The Pre-Stage also captures a Candidate Voice Sample — unpolished natural-language responses to three prompts. This establishes a voice baseline used by the Ghost Editor in Stage 4 to prevent AI-generated text from diverging from the candidate's authentic register.

---

### Stage 0: Intelligence Analyst

Stage 0 produces a Strategic Context Document (SCD): a short intelligence brief contextualizing the job opening within the employer's actual business situation, derived from official sources (SEC filings, earnings calls, Crunchbase, 990s, founder interviews).

**Why this stage exists as a discrete unit:** Job descriptions describe the role as the employer wants it to appear, not necessarily what the business actually needs right now. A company in a defensive pivot has different hiring priorities than the same company's JD template suggests. The SCD surfaces these shadow requirements — implicit hiring needs that emerge from business context but are absent from the JD. Without the SCD, Stage 1's Role Alignment Model and Stage 2's elimination risk assessment operate only on stated requirements, missing the subtext that often determines whether a non-standard candidate gets a callback.

**Safety Default / Logic Fuse:** If no official evidence can be found after exhausting all source types, Stage 0 outputs `INSUFFICIENT EVIDENCE: DEFAULT TO RISK-AVERSE MAINTENANCE POSTURE`. This conservative default propagates downstream — all subsequent stages assume the employer is seeking an exact-match hire with no tolerance for narrative complexity. The system defaults to pessimism, not optimism, when evidence is absent.

---

### Stage 1: Resume Auditor

Stage 1 evaluates candidate-to-JD congruency on paper. It produces a Gap Map, a Micro Fit Score, and an immutable block of Handoff Variables consumed by Stage 2.

**Why this stage exists as a discrete unit:** Stage 1 is deliberately constrained to what is on paper. It does not model how a recruiter will react to what it finds — that is Stage 2's job. This separation is an architectural decision, not an oversight. Conflating paper coverage with screening perception produces contaminated recommendations: a candidate might cover 80% of requirements on paper but still face high elimination risk due to seniority optics or brand mismatch. Keeping the diagnosis clean allows Stage 3 to prescribe with precision rather than guessing which problem it is solving.

The Gap Map cross-references each JD requirement against both the resume and the Work History Document. When a requirement shows None or Partial on the resume but is present in the Work History, it is flagged as a recoverable gap. The count of recoverable gaps is a Handoff Variable — Stage 3 has a mandatory rule that every recoverable gap must receive an Add prescription. None may be left unaddressed.

The Handoff Variables block is marked immutable to prevent downstream stages from re-interpreting Stage 1's findings. Stage 2 and Stage 3 consume it as a fixed input.

---

### Stage 2: Recruiter Simulation

Stage 2 assesses real-world screening likelihood through an adversarial simulation of recruiter and hiring manager behavior. It produces an Elimination Logic Map, a Heuristic Stress Test across two gates, and a Final Diagnostic including Escalation Likelihood.

**Why this stage exists as a discrete unit — and why it deliberately excludes the Work History Document:** The recruiter does not have the Work History Document. Allowing Stage 2 access to it would cause the simulation to evaluate the candidate as they actually are, not as they appear on paper. The stress test must reflect what the screener sees. This is the single most important architectural constraint in the pipeline: the gap between what the candidate has done and what the resume communicates is precisely what Stage 3 exists to close. Stage 2 makes that gap visible by simulating the screening experience without the benefit of context the screener will never have.

The Heuristic Stress Test models two screening gates: a 6-second recruiter screen evaluating headline, summary, and most recent role; and a 3-minute hiring manager skim identifying the First Friction Trigger (where doubt emerges) and First Escalation Trigger (the metric, brand, or scope that compels a callback). These are the two most actionable outputs of the entire pipeline. The stress test is explicitly a structured heuristic, not a validated prediction — it models adversarial pattern-matching behavior, not a probabilistic callback estimate.

---

### Stage 3: Optimization Strategist

Stage 3 is the convergence point. It is the first stage to see all prior outputs simultaneously — Work History Document, SCD, Stage 1 Gap Map and Handoff Variables, Stage 2 Final Diagnostic — and it produces prescriptions for resume modification without drafting any replacement language.

**Why this stage exists as a discrete unit:** Separating diagnosis (Stages 0–2) from prescription (Stage 3) prevents the analytical stages from being contaminated by the desire to find solutions. Stage 3's Delta Assessment first determines whether the optimization is worth doing at all — a Worth-It Verdict of Low ROI or Not Advisable is a legitimate and important output. Candidates should not spend two hours optimizing a resume for a role with fundamental archetype misalignment.

Stage 3 is also the honesty enforcement layer. The Integrity Verdict is non-negotiable: it explicitly classifies each alignment claim as Genuine Alignment (real depth in the Work History), Stretch Claim (partial experience presented as stronger than it is, flagged explicitly), or Hard No (not present in resume or Work History, cannot be honestly claimed). The pipeline cannot prevent a candidate from ignoring this verdict, but it cannot be omitted or softened. Every prescription traces to a specific gap; no prescription requires fabrication.

---

### Stage 4: Ghost Editor (Optional)

Stage 4 produces a job-targeted resume draft that preserves the candidate's authentic voice, using the Voice Profile established from the Pre-Stage Voice Sample. It is positioned as a drafting aid for use under time pressure, not as a submission-ready generator.

**Why this stage is optional:** Stages 0–3 produce everything a candidate needs to edit their own resume: a precise diagnosis, specific prescriptions, and honest constraint boundaries. Stage 4 introduces AI detection risk and voice drift risk. The pipeline's design philosophy is that candidates who write their own edits using Stage 3 prescriptions produce better outcomes than candidates who submit Stage 4 output directly. Stage 4 is included because time constraints are real — but the User Guide is explicit that it should be the exception, not the default.

Stage 4's execution rules enforce that every edit traces to a specific Stage 3 prescription, content is sourced only from the cited Work History section, and anything classified as Stretch or Hard No is replaced with a `[CANDIDATE TO SUPPLY]` placeholder rather than fabricated. The Voice Integrity Check self-audits changed lines against the Voice Sample; if Voice Confidence is Low, the output leads with a warning to treat the draft as a structural outline only.

---

## Data Flow

```
Work History Document (Career Documentarian)
        │
        ├──────────────────────────┐
        │                          │
    Stage 0: SCD              Stage 1: Micro Fit
    Intelligence Analyst       Resume Auditor
    (employer intel)           (paper match + gaps)
        │                          │
        │         ┌────────────────┤
        │         │           Handoff Variables
        │         │                │
        │     Stage 2: Macro Hiring Assessment
        │     Recruiter Simulation
        │     (screening sim — no Work History)
        │         │
        └────┬────┘
             │
         Stage 3: Optimization Triage
         Optimization Strategist
         (prescriptions + honesty check)
             │
         Stage 4: Resume Draft (optional)
         Ghost Editor
         (voice-calibrated draft)
```

Stage 0 and Stage 1 can run in parallel — neither depends on the other's output. Stage 1 uses the SCD if available to inform its Role Alignment Model but can run without it.

Stage 2 requires Stage 1's Handoff Variables. It optionally uses the SCD. It does not receive the Work History Document.

Stage 3 requires Stage 1 Handoff Variables, Stage 2 Final Diagnostic, and the Work History Document. It is the only stage that sees all three simultaneously.

Stage 4 requires Stage 3's Triage Summary and all prior outputs.

---

## Key Design Principles

**1. Archetype mismatch is the primary resume failure mode.** A resume that defaults to one professional framing will trigger recruiter friction before the candidate's strongest signals are reached, even if those signals match the role. Reframing toward the target archetype is the single highest-leverage intervention the pipeline produces.

**2. Diagnosis before prescription.** Analytical stages (0, 1, 2) are structurally separated from prescriptive stages (3, 4). This prevents the desire to find solutions from distorting the factual assessment of the problem.

**3. The resume is the pipeline's weakest input.** Candidates underrepresent their own experience. The Work History Document exists to capture what the resume misses, before any specific application shapes what gets included.

**4. Safety Default / Logic Fuse.** When verified evidence is absent, the system assumes risk-averse employer posture. Optimism in the absence of evidence produces recommendations that fail in practice.

**5. Honesty as a hard constraint.** The pipeline explicitly separates genuine alignment from stretch claims and hard nos. Fabricating or overstating experience is disqualifying; the system is designed to make that boundary visible, not to help candidates obscure it.

**6. Voice anchoring.** Generated or reframed resume content must conform to the candidate's natural writing voice, not mirror JD language. JD language verbatim as bullet headers is a pattern that reads as machine-generated and undermines authenticity.

**7. The recruiter doesn't have your Work History.** Stage 2's exclusion of the Work History Document is a deliberate architectural constraint. The stress test must reflect what the screener sees, not what the candidate knows about themselves.

---

## Known Limitations

**No validation against real recruiter data.** The screening heuristics in Stage 2 are structurally plausible but have not been tested against actual recruiter decision data. No A/B testing has been performed. The stress test models adversarial pattern-matching; it is not a callback probability estimate.

**False precision risk.** The Micro Fit Score's transparent math can create unwarranted confidence. A score of 72 means 72% of stated requirements are covered on paper — not a 72% likelihood of a callback.

**Over-optimization risk.** Running the pipeline against many JDs with Stage 4 enabled may cause candidates to lose their authentic professional voice across iterations.

**AI detection risk.** Stage 4 output may be flagged as machine-generated despite voice calibration. This is a known limitation of any LLM-assisted drafting approach.

**Honesty drift.** The Integrity Verdict is non-negotiable within the pipeline. It cannot prevent a candidate from ignoring it.

**JD URL rendering.** URLs to job board listings typically return near-empty content due to JavaScript rendering. JDs must be pasted directly as plain text.

**Work History is not templated** The input process for work history is set in order of data entry and does not re-sort in chronological order,
