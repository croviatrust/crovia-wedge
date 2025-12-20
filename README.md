# Crovia WEDGE

**Evidence Presence Wedge for AI training transparency.**

Crovia WEDGE is a minimal, non-invasive GitHub Action that answers one
verifiable question:

> **Is there publicly auditable evidence of AI training data usage — or not?**

No simulations.
No assumptions.
No legal claims.

Only **presence or absence of evidence**.

---

## What WEDGE does

Crovia WEDGE runs inside any GitHub workflow and produces a neutral verdict:

- OK — evidence pointer found
- NO — no public evidence pointer
- POINTER — link to external evidence (Open Plane)

It does **not**:
- accuse anyone
- infer intent
- score compliance
- analyze private data

It only reports **what is publicly observable**.

---

## Why WEDGE exists

Most AI pipelines today have:
- no public evidence
- no training receipts
- no auditable trail

WEDGE is designed to be the **first minimal wedge**
that fits into existing CI/CD pipelines
without changing how they work.

---

## Outputs

WEDGE produces:

- a machine-readable verdict
- an optional EVIDENCE.pointer.json
- a neutral signal suitable for:
  - CI checks
  - dashboards
  - transparency reports

Example verdicts:

VERDICT=OK
VERDICT=NO
VERDICT=POINTER

---

## Example usage

- name: Crovia WEDGE — Evidence Presence Check
  uses: croviatrust/crovia-wedge@v1

---

## Philosophy

Crovia WEDGE is intentionally small.

It is not a regulator.
It is not a judge.
It is a sensor.

WEDGE tells you what exists —
and lets others decide what it means.

---

## Part of Crovia

WEDGE is part of the Crovia ecosystem:

CEP Terminal — public inspection
Open Plane — evidence observation
DSSE / Sentinel — advanced analysis (separate layers)

WEDGE always stays neutral.

---

## License

Apache-2.0
