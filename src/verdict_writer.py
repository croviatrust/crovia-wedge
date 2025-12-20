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

status = os.getenv("CROVIA_STATUS", "RED")
reason = os.getenv("CROVIA_REASON", "evidence_absent")
primary = [x for x in os.getenv("CROVIA_PRIMARY", "").split(",") if x]
critical_omissions = int(os.getenv("CROVIA_CRITICAL_OMISSIONS", "0"))
checked = [x for x in os.getenv("CROVIA_CHECKED", "").split(",") if x]

verdict = {
    "schema": "crovia.verdict.v1",
    "timestamp": now,
    "context": "ci",
    "status": status,
    "reason": reason,
    "primary_found": primary,
    "critical_omissions": critical_omissions,
    "artifacts_checked": checked,
    "host": host,
    "run_id": run_id,
}

latest_path = f"{BASE}/verdict_latest.json"
index_path = f"{BASE}/verdict_index.jsonl"

with open(latest_path, "w", encoding="utf-8") as f:
    json.dump(verdict, f, indent=2)

with open(index_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(verdict, ensure_ascii=False) + "\n")

gh_out = os.getenv("GITHUB_OUTPUT")
if gh_out:
    with open(gh_out, "a", encoding="utf-8") as f:
        f.write(f"verdict={status}\n")
        f.write(f"reason={reason}\n")
        f.write(f"primary={','.join(primary)}\n")
        f.write(f"critical_omissions={critical_omissions}\n")
        f.write(f"verdict_path={latest_path}\n")

print(f"[CROVIA] Verdict recorded: {status} ({reason})")
