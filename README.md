# HARIDAS SATHEESH

`// HUMAN NODE ONLINE`

I have no interest in teaching machines to imitate humans.

**I want to know what happens when computation acquires continuity.**

Memory that survives the session. Models that mutate when reality disagrees. Sensors that give software a nervous system. Simulations that let decisions experience consequences before we do. Interfaces where biological signals cross into silicon. Digital systems that remember *why* something happened, not merely that it happened.

None of that requires consciousness.

**But together, it makes ordinary software start looking primitive.**

---

## `// THE MACHINE BOUNDARY`

A neural signal is voltage.  
A meeting is acoustic information.  
A purchase is an event.  
Temperature is molecular motion.  
A decision is a state transition.  
Memory is persisted state.

Different realities become surprisingly similar once they cross the machine boundary.

```text
PHYSICAL / BIOLOGICAL / ORGANIZATIONAL REALITY
                    ↓
              SENSING LAYER
                    ↓
            SIGNAL EXTRACTION
                    ↓
             STATE ESTIMATION
                    ↓
             TEMPORAL MEMORY
                    ↓
               WORLD MODEL
                    ↓
       COUNTERFACTUAL SIMULATION
                    ↓
            UNCERTAINTY GATE
                    ↓
          HUMAN AUTHORIZATION
                    ↓
                ACTUATION
                    ↓
            REALITY CHANGES
                    ↺
```

That loop keeps appearing in almost everything I build.

---

## `// ACTIVE THREADS`

### 01 // ORGANIZATION ↔ MEMORY — [CORTEX](case-studies/cortex-governance-intelligence.md)

Organizations have memory loss.

Decisions decay into meeting transcripts, messages, tickets and somebody's recollection of what happened months ago. CORTEX explores an **organizational memory substrate** where decisions retain provenance, dependencies, reversals and consequences.

Not a chatbot over documents.

**A version-control layer for institutional reality.**

`Architecture / R&D → synthetic benchmark → adversarial evaluation → external review`

### 02 // MIND ↔ MACHINE — [Wireless Brain Interface](case-studies/wireless-brain-interface.md)

The biological brain does not expose an API.

It emits noisy, drifting electrophysiological signals from a system that changes while it is being measured.

`EEG / physiology → latent state → calibrated uncertainty → permission boundary → machine action`

The interesting problem is not decoding a signal once.

**It is keeping the decoder trustworthy while the thing being decoded is changing.**

`Research / Simulation → public-data benchmark → drift + calibration evidence → TBD`

### 03 // HUMAN ↔ DIGITAL CONTINUITY — [Companion Intelligence](case-studies/companion-intelligence-life-os.md)

Most assistants suffer from digital amnesia.

I am exploring what happens when software gains **persistent episodic memory, evidence lineage, temporal context and bounded agency**.

Not an uploaded human. Not artificial consciousness.

Something technically more immediate:

**a computational entity whose present state is causally connected to its own past.**

`In Progress → synthetic governance evidence → broader adversarial evaluation`

### 04 // ENVIRONMENT ↔ ADAPTATION — [Adaptive Personal Cooling](case-studies/adaptive-personal-cooling.md)

Air conditioning treats cubic metres of atmosphere as the patient.

The human is the thermal load that actually matters.

`human microclimate → thermal sensing → state estimation → localized actuation → measured response`

**Don't cool the room. Negotiate with the boundary conditions around the body.**

`Prototype / R&D → instrumented bench validation → measured energy + thermal evidence`

### 05 // FUTURE ↔ DECISION — [Retail Demand Intelligence](case-studies/retail-demand-intelligence.md)

Databases record what happened. They do not record the alternate timeline.

A product with zero sales might have zero demand. Or somebody might have wanted it while it was unavailable.

Same database value. Different universe.

This project investigates the **latent state behind observable events** and what can be tested before intervention.

`Research / Architecture → reproducible public-data benchmark → intervention evidence`

### 06 // MACHINE ↔ PHYSICAL WORLD — [Hardware & IoT](projects/hardware-iot.md)

Raspberry Pi. ESP32-S3. Environmental sensing. Thermal imaging. Edge instrumentation.

Intelligence with no sensory boundary lives inside somebody else's dataset.

**I want computation to touch reality.**

---

## `// THE CHESS PROBLEM`

Prediction is not intelligence. Choosing the locally optimal action is not enough either.

A move modifies the state space from which every later move becomes possible.

So the question is not simply:

`What is the best action?`

It is:

```text
What state exists after the action?
What information becomes observable?
Which branches disappear?
Which branches become reachable?
How expensive is being wrong?
Can the action be reversed?
Should the machine move at all?
```

**I care about machines that can reason about the board, not merely select the next square.**

---

## `// RECURSION`

A system observes reality.

It constructs an internal representation, runs possible futures through it, acts, receives reality's answer and updates itself.

`MODEL(t+1) = f(MODEL(t), REALITY, ERROR, MEMORY)`

But if the architecture responsible for adaptation can itself become an object of measurement, another loop appears:

**the system begins evaluating the machinery by which it evaluates the world.**

That is where things get interesting.

It is also where claims get dangerous.

So this repository has one hard constraint:

## `AMBITION != EVIDENCE`

```text
IDEA
  ↓
RESEARCH
  ↓
SIMULATION
  ↓
PROTOTYPE
  ↓
BENCH VALIDATION
  ↓
EXTERNAL REVIEW
  ↓
REAL-WORLD PILOT
  ↓
PRODUCT CANDIDATE
```

Nothing advances because I want it to.

Synthetic evidence remains synthetic. Unknown measurements remain `TBD`. Failed hypotheses are allowed to fail. Consequential actions keep a human authorization boundary.

**The ambition is allowed to be science fiction. The evidence isn't.**

**Reality gets the final commit.**

---

## `// SYSTEM CONVERGENCE`

These are not isolated projects. They probe different layers of a larger architecture.

```mermaid
flowchart LR
    R["REALITY"] --> S["SENSE"]
    S --> E["ESTIMATE STATE"]
    E --> M["MEMORY"]
    M --> W["WORLD MODEL"]
    W --> X["SIMULATE"]
    X --> U["UNCERTAINTY"]
    U --> H["HUMAN / SAFETY GATE"]
    H --> A["ACT"]
    A --> O["OBSERVE OUTCOME"]
    O --> L["ADAPT"]
    L --> M
```

CORTEX probes memory and provenance. WBI probes biological signal uncertainty. Companion Intelligence probes continuity and bounded agency. Cooling probes adaptive physical control. Retail probes latent-state inference and counterfactual decisions. Hardware gives the stack physical senses.

The long game is understanding what happens when those layers begin to converge — without pretending they already have.

[Open the detailed system map →](diagrams/portfolio-system-map.md)

---

## `// EVIDENCE TERMINAL`

| Experiment | Current boundary | Inspect |
|---|---|---|
| **CORTEX** | Architecture / R&D; synthetic benchmark | [Case study](case-studies/cortex-governance-intelligence.md) · [Benchmark](benchmarks/cortex/README.md) |
| **Wireless Brain Interface** | Research / Simulation | [Case study](case-studies/wireless-brain-interface.md) · [Project](projects/wireless-brain-interface.md) |
| **Companion Intelligence** | In Progress; implementation private | [Case study](case-studies/companion-intelligence-life-os.md) · [Synthetic benchmark](benchmarks/companion-life-os/README.md) |
| **Adaptive Personal Cooling** | Prototype / R&D; bench evidence pending | [Case study](case-studies/adaptive-personal-cooling.md) · [Bench protocol](benchmarks/adaptive-cooling/README.md) |
| **Retail Demand Intelligence** | Research / Architecture | [Case study](case-studies/retail-demand-intelligence.md) · [Benchmark](benchmarks/retail-demand/README.md) |
| **EPMO Microsoft 365 Automation** | Implemented / In Progress | [Case study](case-studies/epmo-automation-portfolio.md) |

---

## `// DEEP STORAGE`

The homepage intentionally exposes only the strongest active threads. The complete portfolio — including professional delivery systems, sustainability, health/performance research, venture explorations, creative work and earlier experiments — remains indexed underneath.

[**Complete Project Index →**](PROJECT_INDEX.md)  
[**Evidence & Status Rules →**](STATUS_AND_EVIDENCE.md)  
[**R&D Roadmap →**](PORTFOLIO_ROADMAP.md)  
[**All Case Studies →**](case-studies/README.md)

---

`// END OF INTRODUCTION`  
`// BEGIN EXPERIMENTS ↓`
