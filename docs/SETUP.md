# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip

## Installation

```bash
# 1. Clone
git clone https://github.com/lakshmipoorani-05/SIEM-Tool.git
cd SIEM-Tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

## Folder Structure After Setup

```
SIEM-Tool/
├── log/         ← DROP .csv log files here
├── processed/   ← Files auto-move here after ingestion
├── anomalies.txt← Auto-created on first anomaly confirmation
└── app.py
```

## Configuring Paths

Default paths are relative. To use absolute Windows paths, edit lines 10–12 in `app.py`:

```python
LOG_FOLDER = r"D:\SIEM\log"
PROCESSED_FOLDER = r"D:\SIEM\processed"
ANOMALY_FILE = r"D:\SIEM\anomalies.txt"
```

## Supported Log Formats

Tested with:
- **Wazuh 4.x** exported CSV alerts (`wazuh-alerts-4.x-*`)
- **CrowdStrike Falcon** on-demand report exports
- Any CSV where threat keywords appear in the row data

## Dashboard Usage

1. Open http://127.0.0.1:5000
2. Drop `.csv` files into the `log/` folder
3. Dashboard auto-refreshes every 5 seconds
4. For flagged rows — click **Yes** to confirm as anomaly, **No** to dismiss
5. All confirmed anomalies are saved to `anomalies.txt`

## Anomaly Log Format

```
[File: report.csv] [ID: 1024] [Category: 🛑 Malware-related activity detected] 
[Timestamp: wazuh-alerts-4.x-2025.06.15] [Event: ip-10-118-1-113.ec2.internal] 
→ 🚨 Marked as anomaly by user (🛑 Malware-related activity detected)
```
