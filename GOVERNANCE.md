# FableBreaker Governance Model

## Overview

FableBreaker operates under a meritocratic governance model designed to ensure benchmark integrity, scientific rigor, and community trust. All decisions affecting the benchmark specification, certification protocol, or scoring methodology follow a structured review and approval process.

---

## Roles and Responsibilities

### Maintainers

Maintainers hold ultimate authority over the benchmark specification and release process.

| Role | Responsibility | Authority |
|------|---------------|-----------|
| **Lead Maintainer** | Strategic direction, final arbitration, release approval | Merge to `main`, specification changes |
| **Core Maintainer** | Day-to-day review, CI/CD, documentation | Merge to `main` with lead approval for spec changes |

**Current Maintainers:**
- Freddy Medina (@FreddyCreates) — Lead Maintainer

### Reviewers

Reviewers are trusted community members who review pull requests and provide domain expertise.

| Reviewer Track | Focus Area |
|----------------|------------|
| **Benchmark Reviewer** | AST language, generator families, scoring protocol |
| **Certification Reviewer** | Evidence packs, hash verification, hidden-seed protocol |
| **Journal Reviewer** | Research papers, methodology, peer review standards |
| **Infrastructure Reviewer** | HTTP service, CI/CD, tooling |

### Contributors

Any community member who submits a pull request, reports an issue, or contributes to discussion.

---

## Decision-Making Process

### Specification Changes (Consensus Required)

Changes to the AST language, scoring formula, or certification protocol require:

1. **RFC Issue** — Open a GitHub Issue tagged `rfc` with a detailed proposal
2. **Review Period** — Minimum 7-day review window for community feedback
3. **Maintainer Approval** — At least one maintainer must approve
4. **No Blocking Objections** — Any maintainer may block with documented technical rationale
5. **Implementation** — Approved RFCs are assigned to a contributor for implementation

### Code Changes (Standard Review)

Standard code changes follow conventional pull request review:

1. **Pull Request** — Submit against the default branch
2. **CI Pass** — All automated checks (lint, test, audit) must pass
3. **Reviewer Approval** — At least one reviewer from the relevant track must approve
4. **Merge** — Maintainer merges after approval

### Emergency Fixes

Critical security or correctness bugs may be merged by any maintainer without the standard review period, provided:

- The fix is minimal and addresses only the vulnerability
- A post-merge review issue is opened within 24 hours
- The fix is announced in the next changelog

---

## Certification Governance

### Seed Authority

Hidden seeds used in certification are controlled exclusively by maintainers. The seed generation and rotation process follows:

1. Seeds are generated using a hardware entropy source
2. Seed commitments (SHA-256 of the seed) are published before certification begins
3. Seeds are revealed after the certification window closes
4. No candidate may request or infer hidden seeds prior to reveal

### Evidence Integrity

All certification evidence packs must include:

- Candidate source code reference (git SHA)
- Dataset generation parameters (seed, count, split)
- Full scoring output with timestamps
- Operator signature (maintainer who ran the certification)

### Dispute Resolution

If a candidate author disputes a certification result:

1. **File a Dispute** — Open an issue tagged `dispute` with the evidence pack reference
2. **Reproduce** — Maintainers independently reproduce the certification run
3. **Arbitration** — Lead maintainer issues a final determination within 14 days
4. **Appeal** — No further appeal is available; disputes are resolved by evidence

---

## Contribution Guidelines

### Candidate Submissions

1. Must expose `evaluate(expr: dict) -> object` as specified in the Candidate Contract
2. Must not access the filesystem, network, or system resources during evaluation
3. Must not import or reference the scorer, generator, or hidden datasets
4. Must pass the full public audit before hidden certification

### New Adversarial Families

1. Must demonstrate a novel failure mode not covered by existing families
2. Must include at least 5 example instances with reference hashes
3. Must not require changes to the AST language specification (unless submitted as an RFC)
4. Must include documentation of the attack vector and expected candidate failure pattern

### Journal Papers

1. Must follow the FableBreaker paper template (HTML format)
2. Must include abstract, methodology, results, and conclusion sections
3. Must cite relevant prior FableBreaker publications
4. Must undergo peer review by at least one Journal Reviewer

---

## Versioning Policy

| Component | Versioning | Compatibility |
|-----------|-----------|---------------|
| AST Language | Semantic (breaking changes = major) | Backward compatible within major |
| Generator | Date-stamped families | New families do not break existing |
| Scorer | Semantic | Output schema stable within major |
| Service API | Prefixed (`/api/v1`) | Old routes maintained for 2 major versions |
| Evidence Pack | Schema versioned | Forward-compatible |

---

## Code of Conduct

All participants in the FableBreaker project are expected to:

1. **Act with scientific integrity** — Do not fabricate results, manipulate benchmarks, or misrepresent performance
2. **Respect the protocol** — Do not attempt to circumvent hidden-seed secrecy or certification requirements
3. **Engage constructively** — Provide specific, evidence-based feedback on technical proposals
4. **Acknowledge contributions** — Credit co-authors, cite prior work, and maintain attribution chains

Violations may result in removal of reviewer status, rejection of submissions, or community ban at maintainer discretion.

---

## Amendments

This governance document may be amended by the Lead Maintainer with a 14-day notice period. Amendments that change decision-making authority require consensus among all maintainers.

---

<p align="center">
  <strong>ItsNotAI LABS</strong><br>
  <em>Governed by evidence. Decided by merit. Verified by proof.</em>
</p>
