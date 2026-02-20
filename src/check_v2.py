"""
Crovia WEDGE v2.0
-----------------

Enhanced evidence presence check with:
- Badge generation for visual status
- Signed pointers for Global Registry
- CFIC integration for certified status
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from badge_generator import CroviaBadgeGenerator
from signed_pointer import SignedPointerGenerator

ROOT = os.getenv("CROVIA_ROOT", ".")
MODE = os.getenv("CROVIA_MODE", "warn").lower()
GENERATE_BADGE = os.getenv("CROVIA_BADGE", "true").lower() == "true"
GENERATE_POINTER = os.getenv("CROVIA_POINTER", "true").lower() == "true"

PRIMARY = [
    "EVIDENCE.json",
    "trust_bundle.v1.json",
    "cep_capsule.v1.json",
    "crovia_manifest.json",
]

CFIC_MARKERS = [
    ".crovia/cfic_certificate.json",
    "CFIC.json",
]


def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def check_evidence():
    """Check for evidence artifacts."""
    found_primary = []
    checked = []
    
    # Check primary artifacts
    for p in PRIMARY:
        checked.append(p)
        if exists(p):
            found_primary.append(p)
    
    # Check receipts*.ndjson anywhere
    for root, _, files in os.walk(ROOT):
        for f in files:
            if f.startswith("receipts") and f.endswith(".ndjson"):
                found_primary.append("receipts*.ndjson")
                checked.append("receipts*.ndjson")
                break
    
    # Check for CFIC certification
    cfic_certified = False
    for marker in CFIC_MARKERS:
        if exists(marker):
            cfic_certified = True
            found_primary.append(f"[CFIC] {marker}")
            break
    
    # Check critical gaps
    critical_omissions = 0
    gap_index = os.path.join(ROOT, "gaps", "gap_index.jsonl")
    checked.append("gaps/gap_index.jsonl")
    
    if os.path.exists(gap_index):
        with open(gap_index, "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                    if o.get("severity", 0) >= 0.8:
                        critical_omissions += 1
                except Exception:
                    pass
    
    return found_primary, checked, critical_omissions, cfic_certified


def main():
    print("\n" + "=" * 50)
    print("  CROVIA WEDGE v2.0")
    print("=" * 50)
    
    found_primary, checked, critical_omissions, cfic_certified = check_evidence()
    
    # Decide verdict
    if not found_primary:
        status = "RED"
        reason = "evidence_absent"
    elif critical_omissions > 0:
        status = "RED"
        reason = "evidence_compromised"
    else:
        status = "GREEN"
        reason = "evidence_recorded"
        if cfic_certified:
            reason = "cfic_certified"
    
    # Export verdict context
    os.environ["CROVIA_STATUS"] = status
    os.environ["CROVIA_REASON"] = reason
    os.environ["CROVIA_PRIMARY"] = ",".join(sorted(set(found_primary)))
    os.environ["CROVIA_CRITICAL_OMISSIONS"] = str(critical_omissions)
    os.environ["CROVIA_CHECKED"] = ",".join(sorted(set(checked)))
    os.environ["CROVIA_CFIC"] = str(cfic_certified).lower()
    
    # Generate badge
    badge_meta = None
    if GENERATE_BADGE:
        print("\n[BADGE] Generating status badge...")
        badge_gen = CroviaBadgeGenerator(os.path.join(ROOT, ".crovia"))
        badge_meta = badge_gen.generate(status, reason, certified=cfic_certified)
        print(f"  SVG: {badge_meta['badge_svg']}")
        print(f"  Embed: {badge_meta['embed_markdown']}")
    
    # Generate signed pointer
    pointer = None
    if GENERATE_POINTER:
        print("\n[POINTER] Generating signed pointer...")
        pointer_gen = SignedPointerGenerator()
        pointer = pointer_gen.generate(
            status=status,
            reason=reason,
            evidence_found=found_primary,
            critical_omissions=critical_omissions,
        )
        pointer_path = pointer_gen.save(pointer, os.path.join(ROOT, ".crovia"))
        print(f"  ID: {pointer.pointer_id}")
        print(f"  Hash: {pointer.observation_hash[:16]}...")
        print(f"  Registry eligible: {pointer.registry_eligible}")
        print(f"  Saved: {pointer_path}")
    
    # Write legacy verdict
    subprocess.check_call([
        sys.executable,
        os.path.join(os.path.dirname(__file__), "verdict_writer.py")
    ])
    
    # Console output
    print("\n" + "-" * 50)
    if status == "GREEN":
        icon = "[OK]" if not cfic_certified else "[CERTIFIED]"
        print(f"  {icon} CROVIA EVIDENCE {status}")
        if cfic_certified:
            print("  Repository has CFIC-certified evidence.")
        else:
            print("  Auditable training evidence detected.")
    else:
        print(f"  [!!] CROVIA EVIDENCE {status}")
        if reason == "evidence_absent":
            print("  No auditable training evidence detected.")
        else:
            print("  Critical omissions detected.")
    
    print("-" * 50)
    
    # Summary
    print("\n[SUMMARY]")
    print(f"  Status: {status}")
    print(f"  Reason: {reason}")
    print(f"  Evidence found: {len(found_primary)}")
    print(f"  CFIC certified: {cfic_certified}")
    if badge_meta:
        print(f"  Badge: {badge_meta['badge_svg']}")
    if pointer:
        print(f"  Pointer: {pointer.pointer_id}")
    
    print("\n" + "=" * 50 + "\n")
    
    # Optional fail
    if status == "RED" and MODE == "fail":
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
