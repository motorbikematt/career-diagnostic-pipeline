Resume Screening Pipeline -- User Guide

1. PURPOSE

This is a diagnostic pipeline for evaluating your fit against a specific job before you apply. It does not write your resume. It tells you whether to apply, what will get you screened out, what to change if you proceed, and where to find the material to make those changes.

The pipeline exists because the most common reason qualified candidates fail to get callbacks is not lack of qualification -- it is that their resume triggers elimination patterns in a screening process they never see. Recruiters spend seconds on initial review. Hiring managers skim for pattern recognition. Both are looking for reasons to discard, not reasons to engage. This pipeline models that reality and gives you a chance to address it before submission.

The system has six stages. One is an initial setup that becomes a living document you maintain over time. One is optional. Four are the core diagnostic sequence you run per job application.


2. OUTCOME

After running the pipeline against a job description, you will have:

- A verified understanding of the employer's strategic context and what kind of hire they actually need.
- A line-by-line map of where your experience matches the job requirements, where it partially matches, and where it is absent.
- A numerical fit score anchored to transparent math you can inspect.
- A heuristic stress test of how a recruiter and hiring manager would process your resume under time pressure, including where they would lose interest and where they would be compelled to call.
- A clear recommendation on whether applying is worth your time.
- If you proceed: a specific list of what to change on your resume, why each change matters, and where in your work history to find the source material for each edit.

You will not have a finished resume. You will have a precise action plan for creating one yourself.


3. WHAT EACH STAGE DOES

Pre-Stage: Career Documentarian (initial setup, maintained over time)
This is an interactive interview session, not a prompt you paste and run. You build it once, then maintain it as a living document. Review and update it every six months, or whenever you change roles, complete a major project, or gain a significant new skill. The output is a structured markdown document organized by role. This document is never sent to employers. It feeds the pipeline.

Stage 0: Strategic Context Document (SCD) Generator
This researches the employer using official sources and produces a short intelligence brief. For public companies, it draws on SEC filings, earnings calls, and press releases. For private companies, startups, and nonprofits, it accepts alternative sources: Crunchbase funding history, 990 filings, founder interviews, grant announcements, and product launch coverage. It identifies the company's current business cycle (growth, efficiency, pivot, maintenance), the hiring manager's likely anxiety, and the type of candidate they need right now. It also surfaces implicit hiring requirements that the JD may not state directly -- the "shadow requirements" that emerge from business context (e.g., a company in defensive pivot mode likely needs someone comfortable with ambiguity and cost discipline, even if the JD only lists technical skills). If no official evidence exists from any source type, the system defaults to assuming the employer is risk-averse and looking for an exact-match hire with no narrative complexity. This default is deliberately conservative. It is better to prepare for a skeptical screener and be pleasantly surprised than to assume a receptive one and get discarded. Note: for early-stage startups and private nonprofits, this default will trigger frequently. The downstream analysis will be conservative as a result, which may overstate elimination risk for employers that are actually in growth mode.

Stage 1: Resume Micro Fit Check
This maps every requirement from the job description against your resume and your Work History Document. It produces a table showing which requirements you match, partially match, or miss entirely. It also identifies "recoverable gaps" -- requirements that are absent from your resume but present in your Work History, meaning you have the experience but have not surfaced it. It scores the fit on a 0-100 scale using weighted math you can inspect: 70 points for hard requirements, 20 for preferred requirements, 10 for qualitative calibration. The output includes a green flag (strongest alignment) and red flag (biggest risk). This stage evaluates only what is on paper. It does not speculate about how a recruiter will react.

Stage 2: Macro Hiring Assessment
This stress-tests your resume against the screening process. It models what kind of recruiter is likely reading your resume based on JD signals, then runs two heuristic gates -- structured approximations of screening behavior, not predictions. Gate 1 is the six-second screen: based on your headline, summary, and most recent role, will the recruiter see a clear match or reach for the next resume? Gate 2 is the three-minute skim: where does a hiring manager first feel doubt, and where does something compel them to pick up the phone? It also assesses hiring manager acceptance risk -- whether you will seem like a safe hire, a high-variance bet, or a threatening peer. It compares you against the likely standard-path applicant. This stage deliberately does not use your Work History. The recruiter does not have it. The stress test must reflect what the recruiter actually sees.

Stage 3: Resume Optimization Triage
This synthesizes everything from Stages 0-2 and your Work History to produce a decision and an action plan. First, it tells you whether editing your resume for this role is worth the effort, rated from High ROI to Not Advisable. Second, it classifies the scope of work required -- from minor bullet reframing to full rewrite. Third, it gives specific prescriptions: which lines to reframe and what they need to signal instead, what to add and where in your Work History to find the source material, what to remove because it creates screening risk, and what to move to the top of the resume to pass the six-second screen. Fourth, it runs an honesty check -- separating genuine alignment from stretch claims from things you cannot honestly assert. Fifth, it identifies information gaps that would need to be resolved before editing. Every prescription states the what and why. None draft replacement language. You write the edits yourself, in your own words.

Stage 4 (Optional): Ghost Editor
This is a drafting tool, not a submission-ready generator. Use it only if you need a working draft under time pressure. It produces a full resume with edits applied, pulling source material from your Work History for any additions. Before writing anything, it analyzes your voice sample from the Pre-Stage to establish your natural sentence structure, vocabulary, tone, and phrasing patterns. Every edit is constrained to match that voice profile. However, even with calibration, AI-generated reframing often shifts tone in ways that are difficult to detect without careful reading. Edits are tagged inline so you can see exactly what changed, what was removed and why, and where you need to supply information the system could not determine. After drafting, it self-audits for voice consistency and flags any lines that diverge from your natural style. It will not claim experience you do not have -- if a prescription requires content classified as a stretch or a hard no, it leaves a placeholder for you to address. If the system determines its output has significant style divergence from your voice, it will warn you explicitly and recommend treating the output as a structural outline rather than a draft. Always compare Stage 4 output against your Pre-Stage Voice Sample before using any of it.


4. WHAT THIS WILL NOT DO

It will not tell you that you are a great fit when you are not. The scoring and simulation are designed to surface uncomfortable truths, not to encourage you.

It will not invent experience you do not have. The honesty check in Stage 3 explicitly separates what you can claim from what you cannot. Stage 4 will leave a placeholder rather than fabricate.

It will not guarantee a callback. The pipeline models screening behavior based on reasonable assumptions, but every hiring process has unknowns -- internal candidates, referral preferences, shifting priorities, human inconsistency. A strong assessment improves your odds. It does not determine the outcome.

It will not replace your judgment about whether a role is right for you. It assesses screening probability, not career fit. A job you would hate but can screen well for will still score well. That is your decision, not the system's.

It will not write your resume for you unless you explicitly use Stage 4, and even then it produces a draft for your review, not a submission-ready document. The pipeline is designed so that you do the writing, guided by specific prescriptions.


5. DANGERS OF USING THIS TOOL

Over-optimization. If you run this pipeline against many job descriptions, you may start unconsciously writing in "what passes screening" mode rather than "what I actually did and how I think about it" mode. The pipeline can tell you what a specific employer wants to hear. It cannot prevent you from losing your authentic professional voice in the process. Use Stage 3 prescriptions as a checklist of problems to solve, not as a template to fill in mechanically.

False precision. The Micro Fit Score is a number on a 0-100 scale with transparent math. That transparency can create false confidence. A score of 72 does not mean you have a 72% chance of getting a callback. It means 72% of the requirements are covered on paper. The Macro assessment is a structured heuristic, not a prediction. Treat all outputs as informed hypotheses, not ground truth.

AI detection risk. Stage 4 generates resume text. Despite voice calibration and integrity checks, there is a nonzero chance that a skilled reader or AI detection tool flags the output as machine-generated. The safest path is to use Stages 0-3 only and write all edits yourself. Stage 4 exists for time pressure situations and should be treated as a draft to be rewritten in your own hand, not submitted verbatim.

Screening stress test fidelity. Stage 2 models recruiter behavior based on structured assumptions about time pressure, pattern matching, and risk aversion. These assumptions are plausible but unvalidated against real recruiter decision data. No A/B testing has been performed. The stress test is a useful heuristic, not a proven predictor. It is most valuable as an adversarial check -- "if a recruiter were this skeptical, would my resume survive?" -- not as a forecast.

Honesty drift. The Honesty Check in Stage 3 draws a line between genuine alignment, stretch claims, and hard nos. But the user makes the final decision about what to put on the resume. The pipeline can flag a stretch claim. It cannot prevent you from ignoring the flag. Over time, especially under job search pressure, the temptation to reframe a "partial" as a "match" increases. The integrity verdict exists to make that temptation visible. Respect it.


6. HOW TO EVALUATE OUTPUT AND PROBLEMS TO LOOK OUT FOR

Stage 0 output: Check the cited sources. If the SCD cites vague or low-quality sources (blog posts from third parties, undated press releases, social media), the business cycle classification may be unreliable. If the Evidence Confidence reads "Default," the system found nothing and is operating in risk-averse mode -- that is fine, but understand that the downstream analysis will be conservative.

Stage 1 output: Inspect the Gap Map before trusting the score. The score is derived from the map, not the other way around. If a requirement is marked "Match" but the evidence column cites tangential experience, the match may be overstated. Pay particular attention to the "In Work History?" column -- a high Recoverable Gaps count means your resume is significantly underrepresenting your actual experience, which is the most actionable finding the pipeline can produce.

Stage 2 output: The most important outputs are the First Friction Trigger and First Escalation Trigger in the Gate 2 stress test. These tell you the specific moment a hiring manager's interest would spike or collapse. If the friction trigger is early in the resume (top-fold), that is a structural problem. If the escalation trigger is buried deep, that is a sequencing problem. Both are directly addressable in Stage 3. Be skeptical of the Recruiter Persona identification -- it is inferred from JD language, which can be misleading (a corporate recruiter may have written a JD that reads like an agency post, or vice versa).

Stage 3 output: The Worth-It Verdict is the first thing to evaluate. If it reads "Not Advisable," seriously consider not applying. The pipeline is telling you that even with edits, the structural mismatch is too large. "Low ROI" means you can apply but should not invest significant time customizing. Focus editing time on "High ROI" and "Moderate ROI" targets. In the Prescriptions, verify that every Add item cites a specific Work History section. If it says "add a bullet about X" without pointing to where that experience lives in your history, the prescription may be aspirational rather than grounded. The Integrity Verdict is non-negotiable -- if it says you cannot honestly claim something, do not claim it.

Stage 4 output: Check the Voice Confidence rating first. "Low" means the draft has significant style divergence and should be treated as an outline, not a draft. Read every [CHANGED] line aloud and ask whether it sounds like something you would write. If it does not, rewrite it. Check every [CANDIDATE TO SUPPLY] tag -- these are places where the system refused to fabricate and needs your input. Do not submit the draft with tags still in place. The edit count at the bottom tells you how much the system changed. If the count is high relative to the resume's total lines, the draft has moved far from your original voice regardless of what the Voice Confidence says.

General: The pipeline's outputs are most reliable when all stages are run in sequence with complete inputs. Skipping Stage 0 triggers the conservative default, which is safe but may cause Stage 2 to overstate elimination risk for companies that are actually in growth mode. Running Stage 1 without the Work History Document removes the Recoverable Gaps detection, which is the pipeline's most differentiated capability. Running Stage 3 without Stage 2 removes the adversarial screening simulation, leaving only paper fit analysis -- useful but incomplete.

If something in the output feels wrong, it probably is. The model is reasoning under uncertainty. Your knowledge of your own career, the employer, and the industry is the final filter. Use the pipeline's structure to organize your thinking, not to replace it.