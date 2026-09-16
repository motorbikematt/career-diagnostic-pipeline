---
document: Work History Document
owner: "Your Name"
version: v1
content_updated: YYYY-MM-DD
structure_updated: YYYY-MM-DD
schema_version: 1
# Canary: a unique token that exists ONLY in this front-matter. The screening
# subagent never receives the WHD; a deterministic post-run scan fails the run
# if this token appears in screen.yaml. The skill generates a fresh random token
# per WHD on first ingest. Never copy it into any downstream artifact.
canary: "WHD-CANARY-REPLACE-WITH-UNIQUE-TOKEN-DO-NOT-OUTPUT"
# One line per role, most recent first. `tags` are 3-5 lowercase capability
# slugs so subagents can retrieve roles selectively without reading the whole
# document. `id` matches the <!-- anchor: role-N --> marker on the role heading.
roles:
  - id: role-1
    company: "Most Recent Company"
    title: "Your Title (or 'Title A to Title B' if promoted)"
    dates: "YYYY-MM to present"
    location: "City, ST"
    tags: [capability-one, capability-two, capability-three]
  # - id: role-2
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

<!-- Each role gets a stable anchor `<!-- anchor: role-N -->` on its heading and
     `<!-- anchor: role-N.project-M -->` on each project, so prescriptions and
     WHD patches can cite machine-resolvable locations. Repeat the block below
     per role, most recent first. -->

<!-- anchor: role-1 -->
# Company Name  |  Your Title

Month YYYY – Month YYYY (or Present)  |  City, ST

## Context

**Company**

- What the company is (stage, size, industry, public/private)
- Your immediate team and org scope

**Reporting Line**

- Who you reported to; notable executive exposure

**Why Joined / Why Left**

- Honest, brief motivations

## Scope

**Hired To Do / What Actually Happened**

- What you were brought in for, and how the role actually unfolded

## Work — Projects & Initiatives

<!-- anchor: role-1.project-1 -->
**1. Project Title**

- Problem: the situation and why it mattered
- Action: what you specifically did (verbs, decisions, scope)
- Outcome: results with concrete numbers where honest and available
- Note: any caveat, e.g. [FLAG: NDA/contract-private - omit figures externally]

<!-- anchor: role-1.project-2 -->
**2. Project Title**

- Problem / Action / Outcome

## Relationships

**Cross-Functional / Executive / External**

- Key working relationships and stakeholders

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

## Education

- Degrees, relevant coursework

## Certifications

- Professional certifications and licenses

## Publications

- Papers, articles, talks (if relevant to your field)

## Patents

- Granted or filed (if any)

## Ongoing Side Projects & Volunteer Work

- Active projects, open source, volunteer roles

## Domain Expertise (Self-Ranked)

- Your deepest areas of expertise, ranked, with the evidence behind each

## Tools & Technologies

**Daily Use / Working Knowledge / Exposure**

- Grouped by depth of familiarity

<!-- anchor: changelog -->
# Changelog

- YYYY-MM-DD - Initial WHD created.
