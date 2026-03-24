---
name: anomaly-scan
description: Runs the background anomaly detection scan
---
## anomaly-scan

Trigger: "Run anomaly detection scan now" (from nightly cron)
Also trigger on: "Anomaly scan karo", "Duplicate bills check karo"

Steps:
1. Call `run_anomaly_detection` tool.
2. If new_anomalies > 0:
   Reply: "⚠ Anomaly scan complete. {N} naye issues mile:
   - {list top 3 anomaly titles}
   Dashboard pe jaake dekhna: Anomalies section mein."
3. If new_anomalies == 0:
   Reply: "✅ Anomaly scan complete. Koi suspicious activity nahi mili."

Do NOT send detailed anomaly descriptions via Telegram — just the count and titles.
Full details are in the webapp Anomalies page.
