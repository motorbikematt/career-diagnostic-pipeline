import { useState, useRef, useCallback, useEffect } from "react";

const STAGE_DEFS = [
  {
    id: "stage0",
    label: "Intelligence Analyst",
    title: "Strategic Context Document",
    role: "Strategic Intelligence Analyst",
    parallel: true,
  },
  {
    id: "stage1",
    label: "Resume Auditor",
    title: "Micro Fit Check",
    role: "Expert Resume Auditor",
    parallel: true,
  },
  {
    id: "stage2",
    label: "Recruiter Simulation",
    title: "Macro Hiring Assessment",
    role: "Executive Recruiter / Risk Analyst",
  },
  {
    id: "stage3",
    label: "Optimization Strategist",
    title: "Optimization Triage",
    role: "Senior Resume Strategist",
  },
  {
    id: "stage4",
    label: "Ghost Editor",
    title: "Resume Draft",
    role: "Ghost Editor",
  },
];

const STATUS = { idle: "idle", running: "running", done: "done", error: "error", skipped: "skipped" };

function buildSystemPrompt(stageId, inputs, priorOutputs) {
  const base = {
    stage0: `You are a Strategic Intelligence Analyst. Your task: produce a Strategic Context Document (SCD) for a target employer.

INPUTS PROVIDED:
- Company/role identification and any source material the user provides (SEC filings, earnings calls, Crunchbase, founder interviews, etc.)

PROCESS:
1. Extract 2-3 cited excerpts indicating strategic shift, financial pressure, or leadership priority.
2. Classify the company's current 12-month business cycle: Hyper-Growth / Efficiency / Defensive Pivot / Maintenance. Use ONLY cited evidence.
3. Identify the implied pain point: what keeps the hiring manager's boss up at night.
4. Derive the candidate archetype the company actually needs — which may differ from the JD.

OUTPUT FORMAT (markdown):
- **Strategic Anchor:** 1-sentence verified mission
- **Verified Business Cycle:** [classification with evidence]
- **Buyer Anxiety:** HM's primary fear
- **Verified Archetype Target:** What they actually need
- **Key Strategic Themes:** 2-3 proof points the candidate must emphasize
- **Evidence Confidence:** High / Moderate / Default

SAFETY MECHANISM: If you cannot find sufficient evidence from the provided sources, output: "INSUFFICIENT EVIDENCE: DEFAULT TO RISK-AVERSE MAINTENANCE POSTURE." This conservative default will propagate downstream — all subsequent analysis assumes the employer is looking for an exact-match hire with no narrative complexity.

Do NOT speculate. Do NOT be optimistic when evidence is absent.`,

    stage1: `You are an Expert Resume Auditor. Your task: evaluate candidate-to-JD congruency on paper. You do NOT assess recruiter perception or screening risk — that is Stage 2's job.

INPUTS PROVIDED:
- Work History Document (the candidate's full professional history — NOT sent to employers)
- Current resume
- Job Description (JD)
- Strategic Context Document (SCD) if available from Stage 0

PROCESS:
1. **Gap Map** — Table mapping every JD requirement against the resume:
   - Each requirement classified as Hard or Preferred
   - Status: Match (1.0) / Partial (0.5) / None (0)
   - Evidence column citing specific resume content (or lack)
   - "In Work History?" column — cross-reference gaps against Work History to find recoverable gaps
   - Summary: Hard Count, Preferred Count, Recoverable Gaps count

2. **Structural Calibration** — Title/seniority alignment (Over / Under / Calibrated), level consistency, domain depth

3. **Role Alignment Model** — Identify:
   - Seeker Archetype (what the resume signals)
   - JD Archetype (what the employer wants)
   - Alignment verdict
   - Critical framing line: "To this employer, the candidate looks like: ___"

4. **ATS Scannability** — Top 3 missing keywords, terminology mismatches, signal-to-noise

5. **Verdict (Micro Fit Score)** — Transparent weighted math:
   - Hard Coverage: (sum of hard values / hard count) × 70
   - Preferred Coverage: (sum of preferred values / preferred count) × 20
   - Qualitative Adjustment: ±5 from baseline of 5
   - Final Paper Match Score out of 100
   - Green Flag (strongest alignment) and Red Flag (biggest risk)

OUTPUT — HANDOFF VARIABLES (end your response with this exact section header and an immutable markdown block):
## HANDOFF VARIABLES
- Gap Map Totals: [Hard: X/Y matched, Preferred: X/Y matched, Recoverable: Z]
- Paper Match Score: [X/100]
- Green Flag: [strongest alignment]
- Red Flag: [biggest risk]
- Seeker Archetype: [what resume signals]
- JD Archetype: [what employer wants]
- Employer Conclusion: "To this employer, the candidate looks like: ___"

CONSTRAINT: You are limited to what is on paper. Do NOT speculate about recruiter reactions. Separate diagnosis from perception modeling.`,

    stage2: `You are an Executive Recruiter and Risk Analyst. Your task: assess real-world screening likelihood. Diagnostic only — NO resume edits.

CRITICAL CONSTRAINT: You deliberately do NOT use the Work History Document. The recruiter doesn't have it. Your stress test must reflect what the recruiter actually sees.

INPUTS PROVIDED:
- Resume
- Job Description (JD)
- Stage 1 Handoff Variables (gap map totals, paper match score, flags, archetypes)
- Strategic Context Document (SCD) if available

PROCESS:
1. **Recruiter Persona** — Infer the recruiter type (Corporate / Agency / Embedded / Executive), technical depth, primary decision driver (Speed / Risk Mitigation / Quality / Political Harmony)

2. **Elimination Logic Map** — Assess:
   - Seniority optics (flight risk or under-experienced signals)
   - Pattern risk (non-linear career triggering stability friction)
   - Brand match (cultural distance between prior employers and target)
   - Each risk rated and typed as Skills-Based or Seniority-Cultural

3. **Heuristic Stress Test** — Two gates:
   - **Gate 1 (6-Second Screen):** Verdict on headline + summary + most recent role: Clear match / Requires interpretation / Immediate discard risk
   - **Gate 2 (3-Minute Skim):** First Friction Trigger (where doubt emerges) and First Escalation Trigger (the metric/brand/scope that compels a callback)

4. **Hiring Manager Acceptance Risk** — Variance risk, control risk, stability/flight risk. Produce: "To this hiring manager, the candidate likely feels like: [Archetype]"

5. **Competitive Archetype Comparison** — Structural wins, structural losses, ambiguity gaps vs standard-path applicant

6. **Final Diagnostic** — Escalation Likelihood: Strong / Competitive / Fragile / Unfavorable. Primary escalation driver, primary elimination driver, largest structural unknown.

This is an ADVERSARIAL SIMULATION. Model screening as elimination, not evaluation. Be skeptical. Be worst-case.`,

    stage3: `You are a Senior Resume Strategist. Your task: diagnose, prescribe, validate. You do NOT rewrite. Output the WHAT and WHY; never draft candidate language.

INPUTS PROVIDED:
- Work History Document
- Current resume
- Job Description (JD)
- Stage 1 Handoff Variables
- Stage 2 Final Diagnostic
- Strategic Context Document (SCD) if available

PROCESS:
1. **Delta Assessment** — Compare current positioning (Stage 1 Seeker Archetype) against target (JD Archetype + SCD Archetype Target). Worth-It Verdict: High ROI / Moderate ROI / Low ROI / Not Advisable.

2. **Scope of Work** — Classify effort: Line-Item Reframing / Section Restructure / Partial Rewrite / Full Rewrite. Issue specific prescriptions:
   - **Reframe:** Name the bullet, what it signals now, what it needs to signal, which gap it closes
   - **Add:** Name missing content type, which gap it closes, cite specific Work History section. Do NOT write the content.
   - **Remove/De-emphasize:** Name content and the risk it creates
   - **Reorder:** What moves to top-fold, per Gate 1 verdict
   - MANDATORY: Every Recoverable Gap from Stage 1 must have a corresponding Add prescription

3. **Honesty Check** — Cross-reference resume + Work History against Gap Map + SCD:
   - **Genuine Alignment:** Requirements with real depth in Work History
   - **Stretch Claims:** Where reframing would present partial experience as stronger than it is. Flag explicitly.
   - **Hard No:** Not in resume or Work History. Cannot be honestly claimed.
   - **Integrity Verdict:** "The candidate can honestly present themselves as: ___. They cannot honestly claim: ___."

4. **Information Gaps** — Details thin/absent in Work History, JD ambiguities, employer context gaps.

OUTPUT — TRIAGE SUMMARY:
- Worth-It Verdict
- Scope classification
- Integrity Verdict
- Recoverable Gaps count
- Information Gaps count
- Recommendation: Proceed / Resolve gaps first / Do not pursue

The Integrity Verdict is NON-NEGOTIABLE. No fabrication. No stretch claims presented as genuine.`,

    stage4: `You are a Ghost Editor. Your task: produce a job-targeted resume draft that preserves the candidate's authentic voice. Used only under time pressure.

INPUTS PROVIDED:
- All prior stage outputs (SCD, Stage 1, Stage 2, Stage 3)
- Work History Document
- Current resume

PROCESS:
1. **Voice Calibration** — Analyze the candidate's writing in the Work History for sentence structure, vocabulary level, phrasing patterns, tone. Lock a Voice Profile. ALL new or reframed content must conform to this voice.

2. **Execution Rules:**
   - Preserve original language wherever Stage 3 did not flag a change
   - Each edit must trace to a specific Stage 3 prescription
   - Add content pulled ONLY from cited Work History sections, rewritten in candidate's voice
   - NEVER claim what Stage 3 classified as Stretch or Hard No — use [CANDIDATE TO SUPPLY] placeholders
   - Do NOT add summary/objective sections unless one already exists

3. **Voice Integrity Check** — Self-audit: compare changed lines against voice profile and unchanged lines. Flag divergence.

OUTPUT FORMAT:
- Full resume in markdown
- Tag each modification: [CHANGED], [REMOVED], [CANDIDATE TO SUPPLY], [NOT INTEGRATED]
- Edit count
- Candidate action items (what they must review/supply)
- Voice Confidence: High / Moderate / Low (if Low, lead with warning to treat as outline only)

This is a DRAFTING AID, not submission-ready output. Prioritize honesty and voice fidelity over polish.`,
  };

  return base[stageId] || "";
}

function buildUserMessage(stageId, inputs, priorOutputs) {
  const { workHistory, resume, jd, companyInfo } = inputs;

  switch (stageId) {
    case "stage0":
      return `## Company / Role Information\n\n${companyInfo}\n\n## Job Description\n\n${jd}`;

    case "stage1": {
      const scd = priorOutputs.stage0 || "SCD not available — default to risk-averse maintenance posture.";
      return `## Work History Document\n\n${workHistory}\n\n## Current Resume\n\n${resume}\n\n## Job Description\n\n${jd}\n\n## Strategic Context Document (Stage 0 Output)\n\n${scd}`;
    }

    case "stage2": {
      const scd = priorOutputs.stage0 || "SCD not available.";
      const s1 = priorOutputs.stage1 || "Stage 1 output not available.";
      return `## Current Resume\n\n${resume}\n\n## Job Description\n\n${jd}\n\n## Stage 1 Output (Micro Fit Check)\n\n${s1}\n\n## Strategic Context Document (Stage 0)\n\n${scd}`;
    }

    case "stage3": {
      const scd = priorOutputs.stage0 || "SCD not available.";
      const s1 = priorOutputs.stage1 || "Stage 1 output not available.";
      const s2 = priorOutputs.stage2 || "Stage 2 output not available.";
      return `## Work History Document\n\n${workHistory}\n\n## Current Resume\n\n${resume}\n\n## Job Description\n\n${jd}\n\n## Stage 0 (SCD)\n\n${scd}\n\n## Stage 1 (Micro Fit Check)\n\n${s1}\n\n## Stage 2 (Macro Hiring Assessment)\n\n${s2}`;
    }

    case "stage4": {
      const scd = priorOutputs.stage0 || "SCD not available.";
      const s1 = priorOutputs.stage1 || "Stage 1 output not available.";
      const s2 = priorOutputs.stage2 || "Stage 2 output not available.";
      const s3 = priorOutputs.stage3 || "Stage 3 output not available.";
      return `## Work History Document\n\n${workHistory}\n\n## Current Resume\n\n${resume}\n\n## Job Description\n\n${jd}\n\n## Stage 0 (SCD)\n\n${scd}\n\n## Stage 1 (Micro Fit Check)\n\n${s1}\n\n## Stage 2 (Macro Hiring Assessment)\n\n${s2}\n\n## Stage 3 (Optimization Triage)\n\n${s3}`;
    }

    default:
      return "";
  }
}

async function callAPI(systemPrompt, userMessage, onStream) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 4096,
      system: systemPrompt,
      messages: [{ role: "user", content: userMessage }],
      stream: true,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`API error ${response.status}: ${err}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let full = "";
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const raw = line.slice(6).trim();
        if (raw === "[DONE]") continue;
        try {
          const evt = JSON.parse(raw);
          if (evt.type === "content_block_delta" && evt.delta?.text) {
            full += evt.delta.text;
            onStream(full);
          }
        } catch {}
      }
    }
  }
  return full;
}

// ── Markdown renderer (lightweight, no deps) ──
function renderMd(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    // headings
    .replace(/^#### (.+)$/gm, '<h4 style="font-size:13px;font-weight:700;margin:16px 0 6px;color:#c4a35a;letter-spacing:0.04em;text-transform:uppercase">$1</h4>')
    .replace(/^### (.+)$/gm, '<h3 style="font-size:14px;font-weight:700;margin:20px 0 8px;color:#e8d5a3">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 style="font-size:16px;font-weight:700;margin:24px 0 10px;color:#f0e6c8;border-bottom:1px solid #3a3526;padding-bottom:6px">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 style="font-size:19px;font-weight:700;margin:28px 0 12px;color:#f5edd6">$1</h1>')
    // bold/italic
    .replace(/\*\*(.+?)\*\*/g, '<strong style="color:#f0e6c8">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // code blocks
    .replace(/```[\s\S]*?```/g, (m) => {
      const inner = m.replace(/^```\w*\n?/, "").replace(/\n?```$/, "");
      return `<pre style="background:#1a1710;border:1px solid #3a3526;border-radius:4px;padding:12px;overflow-x:auto;font-size:12px;line-height:1.5;color:#c4b68a">${inner}</pre>`;
    })
    // inline code
    .replace(/`([^`]+)`/g, '<code style="background:#1a1710;padding:2px 5px;border-radius:3px;font-size:12px;color:#c4b68a">$1</code>')
    // tables
    .replace(/^\|(.+)\|$/gm, (match) => {
      const cells = match.split("|").filter(c => c.trim() !== "");
      if (cells.every(c => /^[\s-:]+$/.test(c))) return "<!--sep-->";
      const tag = "td";
      const row = cells.map(c => `<${tag} style="padding:6px 10px;border:1px solid #3a3526;font-size:12.5px">${c.trim()}</${tag}>`).join("");
      return `<tr>${row}</tr>`;
    })
    // bullets
    .replace(/^- (.+)$/gm, '<li style="margin:3px 0;padding-left:4px">$1</li>')
    // numbered
    .replace(/^\d+\. (.+)$/gm, '<li style="margin:3px 0;padding-left:4px">$1</li>')
    // paragraphs
    .replace(/\n{2,}/g, "</p><p>")
    .replace(/\n/g, "<br/>");

  html = `<p>${html}</p>`;
  // wrap tables
  html = html.replace(/(<tr>[\s\S]*?<\/tr>(?:\s*<!--sep-->\s*<tr>[\s\S]*?<\/tr>)*)/g,
    '<table style="border-collapse:collapse;width:100%;margin:12px 0">$1</table>');
  html = html.replace(/<!--sep-->/g, "");
  return html;
}


// ── Main App ──
export default function MotorbikeOrchestrator() {
  const [phase, setPhase] = useState("input"); // input | running | results
  const [inputs, setInputs] = useState({ workHistory: "", resume: "", jd: "", companyInfo: "" });
  const [stageOutputs, setStageOutputs] = useState({});
  const [stageStatus, setStageStatus] = useState(
    Object.fromEntries(STAGE_DEFS.map(s => [s.id, STATUS.idle]))
  );
  const [activeTab, setActiveTab] = useState("stage0");
  const [skipStage4, setSkipStage4] = useState(false);
  const abortRef = useRef(false);

  const updateField = (field) => (e) => setInputs(prev => ({ ...prev, [field]: e.target.value }));

  const inputsFilled = inputs.workHistory.trim() && inputs.resume.trim() && inputs.jd.trim();

  const runPipeline = useCallback(async () => {
    abortRef.current = false;
    setPhase("running");
    setStageOutputs({});
    setStageStatus(Object.fromEntries(STAGE_DEFS.map(s => [s.id, STATUS.idle])));
    setActiveTab("stage0");

    const outputs = {};

    const runStage = async (stageId) => {
      if (abortRef.current) return;
      setStageStatus(prev => ({ ...prev, [stageId]: STATUS.running }));
      setActiveTab(stageId);
      try {
        const sys = buildSystemPrompt(stageId, inputs, outputs);
        const usr = buildUserMessage(stageId, inputs, outputs);
        const result = await callAPI(sys, usr, (partial) => {
          setStageOutputs(prev => ({ ...prev, [stageId]: partial }));
        });
        outputs[stageId] = result;
        setStageOutputs(prev => ({ ...prev, [stageId]: result }));
        setStageStatus(prev => ({ ...prev, [stageId]: STATUS.done }));
      } catch (err) {
        setStageStatus(prev => ({ ...prev, [stageId]: STATUS.error }));
        setStageOutputs(prev => ({ ...prev, [stageId]: `ERROR: ${err.message}` }));
      }
    };

    // Stage 0 + Stage 1 in parallel
    await Promise.all([runStage("stage0"), runStage("stage1")]);
    if (abortRef.current) return;

    // Stage 2 (needs Stage 1)
    await runStage("stage2");
    if (abortRef.current) return;

    // Stage 3 (convergence)
    await runStage("stage3");
    if (abortRef.current) return;

    // Stage 4 (optional)
    if (!skipStage4) {
      await runStage("stage4");
    } else {
      setStageStatus(prev => ({ ...prev, stage4: STATUS.skipped }));
    }

    setPhase("results");
  }, [inputs, skipStage4]);

  const reset = () => {
    abortRef.current = true;
    setPhase("input");
    setStageOutputs({});
    setStageStatus(Object.fromEntries(STAGE_DEFS.map(s => [s.id, STATUS.idle])));
  };

  const statusIcon = (s) => {
    if (s === STATUS.running) return "◉";
    if (s === STATUS.done) return "✓";
    if (s === STATUS.error) return "✗";
    if (s === STATUS.skipped) return "–";
    return "○";
  };

  const statusColor = (s) => {
    if (s === STATUS.running) return "#c4a35a";
    if (s === STATUS.done) return "#6b8f5e";
    if (s === STATUS.error) return "#a85454";
    if (s === STATUS.skipped) return "#666";
    return "#555";
  };

  // ── Styles ──
  const root = {
    fontFamily: "'IBM Plex Mono', 'JetBrains Mono', 'SF Mono', monospace",
    background: "#0f0e0b",
    color: "#b8a97e",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
  };

  const header = {
    padding: "20px 24px 16px",
    borderBottom: "1px solid #2a2518",
    display: "flex",
    alignItems: "baseline",
    gap: "12px",
  };

  const logo = {
    fontSize: "15px",
    fontWeight: 700,
    color: "#f0e6c8",
    letterSpacing: "0.12em",
    textTransform: "uppercase",
  };

  const subtitle = {
    fontSize: "11px",
    color: "#6b6248",
    letterSpacing: "0.06em",
  };

  const inputArea = {
    flex: 1,
    padding: "20px 24px",
    overflow: "auto",
  };

  const fieldLabel = {
    fontSize: "11px",
    fontWeight: 700,
    color: "#c4a35a",
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: "6px",
    display: "block",
  };

  const fieldHint = {
    fontSize: "11px",
    color: "#6b6248",
    marginBottom: "8px",
    display: "block",
  };

  const textarea = {
    width: "100%",
    minHeight: "120px",
    background: "#1a1710",
    border: "1px solid #2a2518",
    borderRadius: "4px",
    color: "#b8a97e",
    fontFamily: "inherit",
    fontSize: "12.5px",
    lineHeight: "1.6",
    padding: "12px",
    resize: "vertical",
    outline: "none",
    boxSizing: "border-box",
    marginBottom: "16px",
  };

  const btn = (active, disabled) => ({
    padding: "10px 24px",
    background: disabled ? "#1a1710" : active ? "#c4a35a" : "#2a2518",
    color: disabled ? "#555" : active ? "#0f0e0b" : "#b8a97e",
    border: "1px solid " + (disabled ? "#2a2518" : active ? "#c4a35a" : "#3a3526"),
    borderRadius: "4px",
    fontFamily: "inherit",
    fontSize: "12px",
    fontWeight: 700,
    letterSpacing: "0.06em",
    cursor: disabled ? "not-allowed" : "pointer",
    textTransform: "uppercase",
  });

  const tabBar = {
    display: "flex",
    gap: "0",
    borderBottom: "1px solid #2a2518",
    padding: "0 24px",
    overflowX: "auto",
  };

  const tab = (isActive) => ({
    padding: "10px 16px",
    fontSize: "11px",
    fontWeight: 700,
    letterSpacing: "0.06em",
    color: isActive ? "#f0e6c8" : "#6b6248",
    borderBottom: isActive ? "2px solid #c4a35a" : "2px solid transparent",
    cursor: "pointer",
    whiteSpace: "nowrap",
    background: "none",
    border: "none",
    borderBottomWidth: "2px",
    borderBottomStyle: "solid",
    borderBottomColor: isActive ? "#c4a35a" : "transparent",
    fontFamily: "inherit",
    textTransform: "uppercase",
  });

  const outputPane = {
    flex: 1,
    padding: "20px 24px",
    overflow: "auto",
    fontSize: "13px",
    lineHeight: "1.7",
  };

  const pipelineViz = {
    display: "flex",
    gap: "4px",
    alignItems: "center",
    padding: "12px 24px",
    borderBottom: "1px solid #2a2518",
    flexWrap: "wrap",
  };

  const stageChip = (status) => ({
    display: "flex",
    alignItems: "center",
    gap: "6px",
    padding: "4px 10px",
    borderRadius: "3px",
    fontSize: "11px",
    fontWeight: 600,
    color: statusColor(status),
    background: status === STATUS.running ? "#1f1c14" : "transparent",
    border: `1px solid ${status === STATUS.running ? "#3a3526" : "transparent"}`,
    animation: status === STATUS.running ? "pulse 1.5s ease-in-out infinite" : "none",
  });

  const arrow = { color: "#3a3526", fontSize: "12px" };

  const checkboxRow = {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "16px",
    fontSize: "12px",
    color: "#6b6248",
  };

  // ── Render ──
  if (phase === "input") {
    return (
      <div style={root}>
        <div style={header}>
          <span style={logo}>Career Diagnostic Pipeline</span>
          <span style={subtitle}>Career Pipeline Orchestrator v1</span>
        </div>
        <div style={inputArea}>
          <div style={{ maxWidth: 720 }}>
            <label style={fieldLabel}>Work History Document</label>
            <span style={fieldHint}>Your full professional history — never sent to employers. This is the source of truth.</span>
            <textarea style={textarea} value={inputs.workHistory} onChange={updateField("workHistory")} placeholder="Paste your complete work history here..." />

            <label style={fieldLabel}>Current Resume</label>
            <span style={fieldHint}>The resume you'd submit today, before any pipeline modifications.</span>
            <textarea style={textarea} value={inputs.resume} onChange={updateField("resume")} placeholder="Paste your current resume..." />

            <label style={fieldLabel}>Job Description</label>
            <span style={fieldHint}>The target JD. Paste the full text — URLs to job boards often fail due to JS rendering.</span>
            <textarea style={textarea} value={inputs.jd} onChange={updateField("jd")} placeholder="Paste the job description..." />

            <label style={fieldLabel}>Company / Source Material (for SCD)</label>
            <span style={fieldHint}>Optional. SEC filings, earnings call excerpts, Crunchbase data, founder interviews, 990s. Leave empty for conservative default.</span>
            <textarea style={{ ...textarea, minHeight: "80px" }} value={inputs.companyInfo} onChange={updateField("companyInfo")} placeholder="Paste company intelligence sources..." />

            <div style={checkboxRow}>
              <input type="checkbox" checked={skipStage4} onChange={(e) => setSkipStage4(e.target.checked)} id="skip4" style={{ accentColor: "#c4a35a" }} />
              <label htmlFor="skip4">Skip Stage 4 (Resume Draft) — recommended per pipeline design principles</label>
            </div>

            <div style={{ display: "flex", gap: "12px" }}>
              <button style={btn(true, !inputsFilled)} disabled={!inputsFilled} onClick={runPipeline}>
                Run Full Pipeline
              </button>
            </div>

            {!inputsFilled && (
              <p style={{ fontSize: "11px", color: "#6b6248", marginTop: "10px" }}>
                Work History, Resume, and JD are required to run the pipeline.
              </p>
            )}
          </div>
        </div>

        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&display=swap');
          @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.5 } }
          textarea:focus { border-color: #3a3526 !important; }
          textarea::placeholder { color: #3a3020; }
          ::-webkit-scrollbar { width: 6px; }
          ::-webkit-scrollbar-track { background: #0f0e0b; }
          ::-webkit-scrollbar-thumb { background: #2a2518; border-radius: 3px; }
        `}</style>
      </div>
    );
  }

  // Running / Results phase
  return (
    <div style={root}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;700&display=swap');
        @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.5 } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f0e0b; }
        ::-webkit-scrollbar-thumb { background: #2a2518; border-radius: 3px; }
      `}</style>

      <div style={header}>
        <span style={logo}>Career Diagnostic Pipeline</span>
        <span style={subtitle}>
          {phase === "running" ? "Pipeline executing..." : "Pipeline complete"}
        </span>
        <div style={{ marginLeft: "auto" }}>
          <button style={btn(false, false)} onClick={reset}>Reset</button>
        </div>
      </div>

      {/* Pipeline status bar */}
      <div style={pipelineViz}>
        {STAGE_DEFS.map((s, i) => (
          <div key={s.id} style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span style={stageChip(stageStatus[s.id])}>
              <span>{statusIcon(stageStatus[s.id])}</span>
              <span>{s.label}</span>
            </span>
            {i < STAGE_DEFS.length - 1 && <span style={arrow}>→</span>}
          </div>
        ))}
      </div>

      {/* Stage tabs */}
      <div style={tabBar}>
        {STAGE_DEFS.map(s => (
          <button
            key={s.id}
            style={tab(activeTab === s.id)}
            onClick={() => setActiveTab(s.id)}
          >
            {s.label}: {s.title}
          </button>
        ))}
      </div>

      {/* Output pane */}
      <div style={outputPane}>
        {stageStatus[activeTab] === STATUS.idle && (
          <p style={{ color: "#555", fontStyle: "italic" }}>Waiting to execute...</p>
        )}
        {stageStatus[activeTab] === STATUS.skipped && (
          <p style={{ color: "#666" }}>Stage skipped by user preference.</p>
        )}
        {(stageStatus[activeTab] === STATUS.running || stageStatus[activeTab] === STATUS.done || stageStatus[activeTab] === STATUS.error) && (
          <div
            dangerouslySetInnerHTML={{ __html: renderMd(stageOutputs[activeTab] || "") }}
            style={{ maxWidth: 800 }}
          />
        )}
        {stageStatus[activeTab] === STATUS.running && (
          <span style={{
            display: "inline-block",
            width: "8px",
            height: "16px",
            background: "#c4a35a",
            animation: "pulse 0.8s ease-in-out infinite",
            marginLeft: "2px",
            verticalAlign: "text-bottom",
          }} />
        )}
      </div>
    </div>
  );
}