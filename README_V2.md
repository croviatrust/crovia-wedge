# Crovia WEDGE v2.0

> **Evidence Presence Wedge with Badge & Signed Pointers**

## What's New in v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Evidence check | Yes | Yes |
| Visual badge | No | **Yes** |
| Signed pointer | No | **Yes** |
| CFIC integration | No | **Yes** |
| Registry eligible | No | **Yes** |

## Quick Start

```yaml
name: Crovia WEDGE v2.0

on: [push]

jobs:
  wedge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Crovia WEDGE
        uses: croviatrust/crovia-wedge@v2
        with:
          mode: warn
          badge: true
          pointer: true
```

## Outputs

### Badge (`.crovia/badge.svg`)

Embeddable SVG badge for README:

```markdown
[![Crovia Evidence](.crovia/badge.svg)](https://crovia.trust)
```

**Badge States:**
- ![green](https://img.shields.io/badge/crovia-evidence-brightgreen.svg) Evidence recorded
- ![red](https://img.shields.io/badge/crovia-no_evidence-red.svg) No evidence
- ![blue](https://img.shields.io/badge/crovia-certified-blue.svg) CFIC certified

### Signed Pointer (`.crovia/PTR-*.json`)

Cryptographically hashable observation record:

```json
{
  "pointer_id": "PTR-20260110-7A82E05D1E37",
  "schema": "crovia.pointer.v1",
  "observed_at": "2026-01-10T15:10:00Z",
  "repository": "owner/repo",
  "commit_sha": "abc123...",
  "status": "GREEN",
  "reason": "evidence_recorded",
  "observation_hash": "7a82e05d1e37...",
  "registry_eligible": true
}
```

## CFIC Integration

When a repository contains a valid CFIC certificate:

```
.crovia/cfic_certificate.json
```

The badge automatically upgrades to **CERTIFIED** status.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CROVIA_ROOT` | `.` | Root path to scan |
| `CROVIA_MODE` | `warn` | `warn` or `fail` |
| `CROVIA_BADGE` | `true` | Generate badge |
| `CROVIA_POINTER` | `true` | Generate pointer |

## Global Registry

Signed pointers with `registry_eligible: true` can be submitted to the Crovia Global Registry for permanent timestamped record.

```bash
# Submit pointer to registry (coming soon)
crovia register .crovia/PTR-*.json
```

## Migration from v1

v2.0 is backward compatible. Existing workflows continue to work.

To enable new features, add:

```yaml
with:
  badge: true
  pointer: true
```

---

*Part of Crovia Trust Infrastructure*
