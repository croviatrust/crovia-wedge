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

- **GREEN** — auditable evidence was found
- **RED** — no public evidence was observable
- **YELLOW** — evidence present but with critical gaps

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

## Usage

### CLI (available now via crovia-core-engine)

```bash
# Install
pip install crovia

# Scan current directory for evidence artifacts
crovia wedge scan

# Scan a specific project directory
crovia wedge scan --path ./my-ai-project

# One-line status
crovia wedge status

# Fail if no evidence found (for CI scripts)
crovia wedge scan --mode fail

# Explain what artifacts Crovia looks for
crovia wedge explain
```

### GitHub Action (available now)

```yaml
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
          mode: warn   # or: fail
          root: .      # directory to scan
```

Outputs you can use in subsequent steps:

```yaml
      - name: Fail if no evidence found
        if: steps.wedge.outputs.verdict == 'RED'
        run: exit 1
```

> `version: 2` (badge + signed pointer generation) is in development.

### CI via CLI (alternative)

```yaml
jobs:
  wedge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Crovia
        run: pip install crovia

      - name: Run WEDGE scan
        run: crovia wedge scan --mode fail
```

---

## Philosophy

Crovia WEDGE is intentionally small.

It is not a regulator.  
It is not a judge.  
It is a **sensor**.

WEDGE tells you what exists — and lets others decide what it means.

---

## Part of Crovia

WEDGE is part of the Crovia open core:

- [crovia-core-engine](https://github.com/croviatrust/crovia-core-engine) — CLI + CRC-1 evidence pipeline
- [crovia-evidence-lab](https://github.com/croviatrust/crovia-evidence-lab) — public evidence artifacts
- [Live Registry](https://registry.croviatrust.com/registry/) — real-time observation stream

Each layer remains independent.

---

## License

Apache-2.0
