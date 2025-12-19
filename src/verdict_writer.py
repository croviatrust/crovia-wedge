import json
import os
import socket
import uuid
from datetime import datetime, timezone

BASE = ".crovia/verdicts"
os.makedirs(BASE, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()
run_id = os.getenv("GITHUB_RUN_ID", str(uuid.uuid4()))
host = socket.gethostname()

verdict = {
    "schema": "crovia.verdict.v1",
    "timestamp": now,
    "context": "ci",
    "status": os.getenv("CROVIA_STATUS", "RED"),
    "reason": os.getenv("CROVIA_REASON", "evidence_absent"),
    "primary_found": [x for x in os.getenv("CROVIA_PRIMARY", "").split(",") if x],
    "critical_omissions": int(os.getenv("CROVIA_CRITICAL_OMISSIONS", "0")),
    "artifacts_checked": [x for x in os.getenv("CROVIA_CHECKED", "").split(",") if x],
    "host": host,
    "run_id": run_id
}

# Write latest verdict
with open(f"{BASE}/verdict_latest.json", "w", encoding="utf-8") as f:
    json.dump(verdict, f, indent=2)

# Append to verdict library
with open(f"{BASE}/verdict_index.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(verdict) + "\n")

print(f"[CROVIA] Verdict recorded: {verdict['status']}")
