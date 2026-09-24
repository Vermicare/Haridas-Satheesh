# Companion Intelligence — Life OS

**Status:** In Progress / Independent Engineering Project  
**Repository:** Private

Companion Intelligence is a long-term Personal Operating System designed to help people make healthier, wiser and more autonomous decisions while preserving privacy, dignity and human agency.

## System domains

1. **Life Operating System** — goals, commitments, routines, constraints and context.
2. **Knowledge System** — capture, retrieval, versioning and provenance.
3. **Reasoning Engine** — planning, analysis, uncertainty and decision support.
4. **Execution Engine (Spider)** — bounded, explicitly authorized actions.
5. **Learning Engine** — evaluates outcomes and improves future decisions.

## Engineering principles
- human autonomy over automation,
- privacy and security by design,
- explicit consent for consequential actions,
- evidence over assumptions,
- transparent uncertainty and provenance,
- modular and replaceable components,
- progressive delivery,
- no covert persuasion or dark patterns.

---

## Recovered early workstreams

The project evolved through several named workstreams before the current architecture stabilized.

### Minimum Viable Companion
**Status:** Early Product / Architecture Workstream

Focused on defining the smallest useful personal-intelligence system before expanding into a broader Life OS.

### Kingdom Graph
**Status:** Architecture / Knowledge Representation

Early graph-oriented model for representing important life domains, relationships, commitments and context.

### Daily Brief
**Status:** Product / Workflow Concept

A concise daily synthesis of priorities, context, evidence and recommended next actions.

### Weekly Kingdom Review
**Status:** Product / Workflow Concept

A periodic review layer intended to summarize changes across projects, health, career, commitments and longer-term goals.

### Life Seasons Guided Journey
**Status:** Product / UX Workstream

A guided structure for helping the user move through different life phases and priorities rather than treating every goal as equally active at all times.

### First-run Onboarding
**Status:** Product / UX Workstream

Onboarding flow intended to establish trusted context, permissions and system expectations safely.

### Standalone Tester
**Status:** Engineering Workstream

A standalone test surface used to validate system behavior outside the main application flow.

### Specialist Agents
**Status:** Architecture / Agent Workstream

Specialized agents for bounded domains rather than one unrestricted general-purpose executor.

### Human OS / Health OS / Athlete OS
**Status:** Architecture Evolution

Related operating-system concepts that explored domain-specific personal intelligence for general life, health and athletic performance.

### Constitution / System Specification
**Status:** Governance / Architecture

A formal specification of system principles, boundaries, permissions, privacy, agency and architectural rules.

### Roadmap & Execution Workflows
**Status:** Program / Delivery Architecture

Structured sequencing for engineering outcomes, milestones, ADRs and bounded execution.

---

## Spider Execution Engine
**Status:** In Progress

Execution component designed around explicit authorization, auditability and bounded actions rather than uncontrolled autonomy.

---

## Career & Income Decision Workspace
**Status:** Implemented / In Progress

Decision-support workspace comparing:
- current-role growth,
- international opportunities,
- external-income paths,
- evidence,
- confidence,
- assumptions,
- reversal conditions.

---

## AI Architect Agent
**Status:** Prototype / Engineering Workflow

A bounded architecture-review workflow for code changes with safeguards around secrets, storage and automatic modification.

---

## Evidence Conflict & Supersession
**Status:** Implemented / Engineering

Mechanisms for:
- conflicting evidence detection,
- explicit supersession,
- claim approval,
- binding newer decision versions to accepted evidence.

---

## Knowledge Inbox & Approval
**Status:** Implemented / Engineering

A controlled intake pattern where evidence is ingested, reviewed and explicitly accepted before becoming trusted decision context.

---

## Read-only Knowledge Source Boundary
**Status:** Engineering Architecture

External knowledge connectors remain read-only unless an action is explicitly authorized.

---

## SQLCipher Research Probe
**Status:** Research / Prototype

Encrypted local-storage and backup exploration.

---

## Production Encrypted Store Evaluation
**Status:** Research / Engineering

Evaluation work around production-grade encrypted storage, backup integrity and failure handling.

---

## Atomic Record / Receipt Transactions
**Status:** Engineering Research

Reliability work focused on making important writes and receipts atomic and auditable.

---

## Linux Secret Service Key-Custody Probe
**Status:** Research / Prototype

Credential-security experiment for local key handling.

---

## Cross-platform Packaging & Interaction Simulation
**Status:** Engineering Work

Packaging and test work across Windows, macOS and Linux, including interaction simulation and CI/release considerations.
