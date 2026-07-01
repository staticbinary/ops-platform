#!/usr/bin/env bash
set -euo pipefail

echo "Validating Grafana provisioning files..."

test -f infrastructure/grafana/provisioning/datasources/datasources.yml
test -f infrastructure/grafana/provisioning/dashboards/dashboards.yml
test -f infrastructure/grafana/provisioning/alerting/contact-points.yml
test -f infrastructure/grafana/provisioning/alerting/notification-policies.yml
test -f infrastructure/grafana/provisioning/alerting/templates.yml

python - <<'PY'
import json
from pathlib import Path

dashboard_dir = Path("infrastructure/grafana/dashboards")
dashboards = sorted(dashboard_dir.glob("*.json"))

if not dashboards:
    raise SystemExit("No Grafana dashboard JSON files found")

seen = set()

for path in dashboards:
    data = json.loads(path.read_text())

    if "spec" in data:
        uid = data.get("metadata", {}).get("name")
        title = data.get("spec", {}).get("title")
    else:
        uid = data.get("uid")
        title = data.get("title")

    if not uid:
        raise SystemExit(f"{path} missing dashboard UID")

    if not title:
        raise SystemExit(f"{path} missing dashboard title")

    if uid in seen:
        raise SystemExit(f"Duplicate dashboard UID detected: {uid}")

    seen.add(uid)

print(f"Validated {len(dashboards)} Grafana dashboards")
PY

echo "Grafana provisioning validation successful."
