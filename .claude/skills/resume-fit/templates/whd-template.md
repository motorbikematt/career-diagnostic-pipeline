---
document: Work History Document
owner: "Your Name"
version: v1
content_updated: YYYY-MM-DD
structure_updated: YYYY-MM-DD
schema_version: 1
# Canary: a unique token that exists ONLY in this front-matter. The screening
# subagent never receives the WHD; a deterministic post-run scan fails the run
# if this token appears in screen.yaml. Generate a fresh random token with
# `python .claude/skills/resume-fit/helpers/canary.py init <whd.md>`; the scan
# refuses to run on this placeholder. Never copy it into any downstream artifact.
canary: "WHD-CANARY-REPLACE-WITH-UNIQUE-TOKEN-DO-NOT-OUTPUT"
# One line per role, most recent first. `tags` are 3-5 lowercase capability
# slugs so subagents can retrieve roles selectively without reading the whole
# document. `id` is the role's stable slug (the company name, e.g. `acme-robotics`) and
# matches the anchor marker line on the role heading. Ids never renumber.
roles:
  - id: company-name
    company: "Most Recent Company"
    title: "Your Title (or 'Title A to Title B' if promoted)"
    dates: "YYYY-MM to present"
    location: "City, ST"
    # include: normal resume entry | context-only: may shape the summary or
    # origin story, never a dated resume line (old roles, age signal) |
    # omit: left off unless a JD makes it relevant, then only with confirmation
    resume_default: include
    resume_note: ""
    tags: [capability-one, capability-two, capability-three]
  # - id: earlier-company
  #   company: "..."
  #   ...
special_sections:
  - id: voice-sample
    editable: false
    note: "Voice calibration source for drafting; the reconciliation loop never edits it."
  - id: beyond-employment
  - id: changelog
---

**WORK HISTORY DOCUMENT**

**Your Name**

email  •  phone  •  linkedin.com/in/you

*Source of truth for all downstream resume stages. Not for external distribution.*

<!-- Anchors are one-line marker lines (hidden by markdown viewers) with stable
     slug ids: `company-name` on the role heading, `company-name.<section>` on
     each ## subsection, `company-name.pN` on project N. Prescriptions and WHD
     patches cite them. Repeat the block below per role, most recent first.
     A legacy WHD without anchors: run helpers/whd_migrate.py. -->

<!-- anchor: company-name -->
# Company Name  |  Your Title

Month YYYY – Month YYYY (or Present)  |  City, ST

<!-- anchor: company-name.context -->
## Context

**Company**

- What the company is (stage, size, industry, public/private)
- Your immediate team and org scope

**Reporting Line**

- Who you reported to; notable executive exposure

**Why Joined / Why Left**

- Honest, brief motivations

<!-- anchor: company-name.scope -->
## Scope

**Hired To Do / What Actually Happened**

- What you were brought in for, and how the role actually unfolded

<!-- anchor: company-name.work -->
## Work — Projects & Initiatives

<!-- anchor: company-name.p1 -->
**1. Project Title**

- Problem: the situation and why it mattered
- Action: what you specifically did (verbs, decisions, scope)
- Outcome: results with concrete numbers where honest and available
- Note: any caveat, e.g. [FLAG: NDA/contract-private - omit figures externally]

<!-- anchor: company-name.p2 -->
**2. Project Title**

- Problem / Action / Outcome

<!-- anchor: company-name.relationships -->
## Relationships

**Cross-Functional / Executive / External**

- Key working relationships and stakeholders

<!-- anchor: company-name.self-assessment -->
## Candid Self-Assessment

**Most Proud Of**

- Honest high point

**What Did Not Go Well**

- Honest shortfall (this candor is what keeps the WHD trustworthy)

**Skills Built**

- Durable capabilities gained in this role

<!-- anchor: voice-sample -->
# Candidate Voice Sample

Stored as the drafting voice baseline. Raw, unpolished responses in your own words.
Answer conversationally; do not edit for polish. The finishing loop never rewrites
this section — it calibrates against it.

## Q1: Describe what you do professionally as if telling a friend at a bar.

*Your answer, in your own voice.*

## Q2: What is the hardest work problem you have solved and how did you approach it?

*Your answer.*

## Q3: What kind of work environment brings out your best performance?

*Your answer.*

<!-- anchor: beyond-employment -->
# Beyond Employment

<!-- anchor: beyond-employment.education -->
## Education

- Degrees, relevant coursework

<!-- anchor: beyond-employment.certifications -->
## Certifications

- Professional certifications and licenses

<!-- anchor: beyond-employment.publications -->
## Publications

- Papers, articles, talks (if relevant to your field)

<!-- anchor: beyond-employment.patents -->
## Patents

- Granted or filed (if any)

<!-- anchor: beyond-employment.side-projects -->
## Ongoing Side Projects & Volunteer Work

- Active projects, open source, volunteer roles

<!-- anchor: beyond-employment.domain-expertise -->
## Domain Expertise (Self-Ranked)

- Your deepest areas of expertise, ranked, with the evidence behind each

<!-- anchor: beyond-employment.tools -->
## Tools & Technologies

**Daily Use / Working Knowledge / Exposure**

- Grouped by depth of familiarity

<!-- anchor: changelog -->
# Changelog

- YYYY-MM-DD - Initial WHD created.
