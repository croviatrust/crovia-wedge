# Crovia WEDGE

**Evidence Presence Wedge for AI training transparency.**

Crovia WEDGE is a minimal, non-invasive GitHub Action that answers one verifiable question:

> **Is there publicly auditable evidence of AI training data usage — or not?**

No simulations.  
No assumptions.  
No legal claims.

Only **presence or absence of evidence**.

---

## What WEDGE does

Crovia WEDGE runs inside any GitHub workflow and observes whether publicly auditable AI training evidence is present at a given location and time.

It produces a **neutral observation**, not an interpretation.

Possible outcomes:

- **OK** — auditable evidence was found
- **NO** — no public evidence was observable
- **POINTER** — absence observed, with a pointer to the observation context

WEDGE does **not**:
- accuse anyone
- infer intent
- score compliance
- analyze private data

It only reports **what is publicly observable**.

---

## Why WEDGE exists

Most AI pipelines today have:

- no public evidence of training data usage
- no receipts
- no auditable trail

As a result, **absence of evidence is invisible**.

WEDGE makes that absence **observable, recordable, and repeatable** without changing how existing CI/CD pipelines work.

---

## Outputs

WEDGE produces:

- a machine-readable verdict (`OK` / `NO`)
- an optional `EVIDENCE.pointer.json` when absence is observed
- a neutral signal suitable for:
  - CI checks
  - dashboards
  - transparency reports

When absence is observed, the pointer records **where and when** no public evidence was observable — without attribution or accusation.

---

## Example usage

    name: Crovia WEDGE — Evidence Presence Check

    on: [push]

    jobs:
      wedge:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - name: Run Crovia WEDGE
            uses: croviatrust/crovia-wedge@v1
            with:
              mode: warn
              root: .

The workflow can optionally react to the verdict using outputs, but WEDGE itself remains neutral.

---

## Using outputs in CI (optional)

WEDGE exposes outputs you can use in your workflow:

- `verdict` (`GREEN` / `RED`)
- `reason` (`evidence_recorded` / `evidence_absent` / `evidence_compromised`)
- `primary` (comma-separated)
- `critical_omissions` (integer)
- `verdict_path` (path to `.crovia/verdicts/verdict_latest.json`)
- `pointer` (present only when `RED`, points to `EVIDENCE.pointer.json`)

Example (fail only when evidence is absent):

    jobs:
      wedge:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - name: Run Crovia WEDGE
            id: wedge
            uses: croviatrust/crovia-wedge@v1
            with:
              mode: warn

          - name: Fail if evidence is absent
            if: steps.wedge.outputs.verdict == 'RED' && steps.wedge.outputs.reason == 'evidence_absent'
            run: exit 1

---

## Philosophy

Crovia WEDGE is intentionally small.

It is not a regulator.  
It is not a judge.  
It is a **sensor**.

WEDGE tells you what exists — and lets others decide what it means.

---

## Part of Crovia

WEDGE is part of the Crovia ecosystem:

- **CEP Terminal** — public inspection
- **Open Plane / Hubble Continuum** — evidence observation over time
- **DSSE / Sentinel** — advanced analysis (separate layers)

Each layer remains independent.

---

## License

Apache-2.0
