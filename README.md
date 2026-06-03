# 🔍 SIEM Log Analysis Dashboard

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat&logo=flask&logoColor=white)
![Wazuh](https://img.shields.io/badge/Wazuh-Integrated-3AAFA9?style=flat)
![CrowdStrike](https://img.shields.io/badge/CrowdStrike-Log%20Support-E3001B?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

A real-time **Security Information and Event Management (SIEM)** dashboard built with Flask. Monitors incoming CSV log files from Wazuh/CrowdStrike, detects threats using rule-based analysis, and allows human-in-the-loop anomaly verification — all in a dark-mode web UI.

---

## 📸 Dashboard Preview

> Dark-mode real-time log table with threat categorization and one-click anomaly marking.

```
🔍 Real-Time SIEM Log Dashboard
┌──────────────┬────────────┬──────────┬───────────────────────────────┬──────────┐
│ File         │ Timestamp  │ Source   │ Analysis                      │ Verify   │
├──────────────┼────────────┼──────────┼───────────────────────────────┼──────────┤
│ report.csv   │ 2025-06-15 │ ec2-host │ 🛑 Malware-related activity   │ [Yes][No]│
│ report.csv   │ 2025-06-16 │ ec2-host │ ✅ No anomalies detected       │          │
└──────────────┴────────────┴──────────┴───────────────────────────────┴──────────┘
```

---

## 🚀 Features

- **Real-Time Log Monitoring** — watches a folder for new `.csv` log files and ingests them automatically via a background thread
- **Offline Threat Detection** — rule-based analyzer flags:
  - ⚠️ Security issues (errors, unauthorized access, failures)
  - 🚫 Multiple failed login attempts
  - 🛑 Malware/virus-related activity
  - 🚨 Possible DoS/attack patterns
- **Human-in-the-Loop Verification** — analysts click Yes/No to confirm or dismiss each flagged alert
- **Anomaly Logging** — every confirmed anomaly is appended to `anomalies.txt` with full context (file, ID, category, timestamp, event)
- **Processed File Management** — after ingestion, log files are automatically moved from `log/` to `processed/` to prevent re-processing
- **REST API** — `/api/logs` endpoint returns all current log entries as JSON
- **AI + LLM Architecture** — designed as Phase 1 (rule-based AI) of a two-phase system; Phase 2 integrates an LLM for deeper contextual analysis (see [Architecture](#-architecture))

---

## 🗂️ Project Structure

```
SIEM-Tool/
├── app.py                  # Main Flask application
├── anomalies.txt           # Auto-generated anomaly log (git-ignored)
├── log/                    # Drop incoming .csv log files here
│   └── .gitkeep
├── processed/              # Processed logs are moved here automatically
│   └── .gitkeep
├── docs/
│   └── AI_MODEL_AND_LLM_MODEL_IN_SIEM.md   # Architecture documentation
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Prerequisites
```bash
python --version   # needs Python 3.9+
pip install flask
```

### 2. Clone the repo
```bash
git clone https://github.com/lakshmipoorani-05/SIEM-Tool.git
cd SIEM-Tool
```

### 3. (Optional) Configure paths

By default the app uses relative paths. To point to a custom location, edit these lines in `app.py`:
```python
LOG_FOLDER = r"D:\SIEM\log"         # change to your log folder
PROCESSED_FOLDER = r"D:\SIEM\processed"
ANOMALY_FILE = r"D:\SIEM\anomalies.txt"
```

### 4. Run
```bash
python app.py
```

Open your browser at → **http://127.0.0.1:5000**

### 5. Feed logs
Drop any `.csv` log file (Wazuh/CrowdStrike export format) into the `log/` folder. The dashboard auto-refreshes every 5 seconds.

---

## 🧠 Architecture

### Phase 1 — Rule-Based AI Analyzer (Implemented)

The `analyze_log_offline()` function acts as a pre-filter. It scans each log row for known threat keywords and assigns a category label before the human analyst sees it.

```
Raw CSV Logs → Keyword Analyzer → Category Tags → Dashboard Table → Human Verify → anomalies.txt
```

**Threat categories detected:**
| Pattern | Label |
|---|---|
| `error`, `failed`, `unauthorized` | ⚠️ Security issue detected |
| `login failed` | 🚫 Multiple failed login attempts |
| `malware`, `virus` | 🛑 Malware-related activity detected |
| `attack`, `dos` | 🚨 Possible DoS attack detected |

### Phase 2 — LLM Integration (Designed)

Flagged logs from Phase 1 are forwarded to an LLM (e.g., Claude/GPT) for:
- **Classification validation** — is this a true positive or false positive?
- **Context-aware explanation** — e.g., "Login from India and Germany within 3 minutes = impossible travel"
- **Remediation suggestions** — block IP, force password reset, etc.

See [`docs/AI_MODEL_AND_LLM_MODEL_IN_SIEM.md`](docs/AI_MODEL_AND_LLM_MODEL_IN_SIEM.md) for the full design.

---

## 📊 Log Format Support

Built and tested with exported Wazuh 4.x + CrowdStrike Falcon log CSVs. Key columns used:

| Column Index | Field |
|---|---|
| 0 | `_index` (timestamp/index name) |
| 2 | `agent.name` (source host) |
| 6 | `manager.name` / event source |
| 13 | `rule.level` (severity) |

The analyzer scans the **full row string**, so it works with any CSV where threat keywords appear in the data.

---

## 📁 Sample Data

Real Wazuh alert data used during development includes CrowdStrike `ScheduledReportNotificationEvent` and Netskope SSE logs from an EC2-based SIEM deployment (`ip-10-118-1-113.ec2.internal`). Sample files are **not included** in this repo to avoid exposing sensitive infrastructure data.

---

## 🔌 API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard UI |
| `/api/logs` | GET | Returns all logs as JSON |
| `/verify/<id>` | POST | Mark a log as anomaly (`yes`) or safe (`no`) |

---

## 🛣️ Roadmap

- [x] Real-time folder watcher
- [x] Rule-based threat detection
- [x] Human verification workflow
- [x] Anomaly persistence to file
- [x] Processed file archival
- [ ] LLM integration for contextual analysis
- [ ] Impossible travel detection (geo-IP comparison)
- [ ] Email/Slack alert on critical anomalies
- [ ] SQLite persistence (replace in-memory list)
- [ ] Multi-user role support (Admin / Analyst)

---

## 👩‍💻 Author

**Lakshmi Poorani**  
B.E. CSE + BS Data Science — IIT Madras  
[GitHub](https://github.com/lakshmipoorani-05) · [LinkedIn](https://linkedin.com/in/lakshmipoorani)

Built during internship work at **Navitas Life Sciences**, processing real Wazuh + CrowdStrike SIEM alert data.

---

## 📄 License

MIT License — use freely, credit appreciated.
