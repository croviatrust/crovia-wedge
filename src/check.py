import os
import sys
import json
import subprocess

ROOT = os.getenv("CROVIA_ROOT", ".")
MODE = os.getenv("CROVIA_MODE", "warn").lower()

PRIMARY = [
    "EVIDENCE.json",
    "trust_bundle.v1.json",
    "cep_capsule.v1.json",
]

found_primary = []
checked = []

def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))

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

# Export verdict context
os.environ["CROVIA_STATUS"] = status
os.environ["CROVIA_REASON"] = reason
os.environ["CROVIA_PRIMARY"] = ",".join(sorted(set(found_primary)))
os.environ["CROVIA_CRITICAL_OMISSIONS"] = str(critical_omissions)
os.environ["CROVIA_CHECKED"] = ",".join(sorted(set(checked)))

# Write verdict
subprocess.check_call([
    sys.executable,
    os.path.join(os.path.dirname(__file__), "verdict_writer.py")
])

# Console output (Crovia style)
print("\n────────────────────────────────────────")
print(f"CROVIA · EVIDENCE {status}")
print("────────────────────────────────────────")

if status == "GREEN":
    print("Auditable training evidence detected.")
else:
    if reason == "evidence_absent":
        print("No auditable training evidence detected.")
    else:
        print("Critical omissions detected.")

print("\nVerdict recorded.\n")

# Optional fail
if status == "RED" and MODE == "fail":
    sys.exit(1)

sys.exit(0)
