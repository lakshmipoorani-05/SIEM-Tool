from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import os
import time
import threading
import queue
import csv
import shutil  # for moving files

# ===== CONFIGURATION =====
LOG_FOLDER = r"D:\SIEM\log"
PROCESSED_FOLDER = r"D:\SIEM\processed"   # folder for processed logs
ANOMALY_FILE = r"D:\SIEM\anomalies.txt"
CHECK_INTERVAL = 2  # seconds

# ===== SIMPLE OFFLINE ANALYZER =====
def analyze_log_offline(row):
    alerts = []
    row_str = " ".join(row).lower()

    if "error" in row_str or "failed" in row_str or "unauthorized" in row_str:
        alerts.append("⚠️ Security issue detected")
    if "login failed" in row_str:
        alerts.append("🚫 Multiple failed login attempts")
    if "malware" in row_str or "virus" in row_str:
        alerts.append("🛑 Malware-related activity detected")
    if "attack" in row_str or "dos" in row_str:
        alerts.append("🚨 Possible DoS attack detected")

    if not alerts:
        alerts.append("✅ No anomalies detected")

    return alerts

# ===== FOLDER MONITOR THREAD =====
log_queue = queue.Queue()
seen_files = set()

def monitor_logs():
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)  # ensure folder exists

    while True:
        try:
            for filename in os.listdir(LOG_FOLDER):
                filepath = os.path.join(LOG_FOLDER, filename)

                if filepath not in seen_files and os.path.isfile(filepath):
                    seen_files.add(filepath)

                    temp_logs = []  # collect logs before moving file

                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        reader = csv.reader(f)
                        headers = next(reader, None)  # skip header if exists
                        for row in reader:
                            if row:  # skip empty lines
                                reasons = analyze_log_offline(row)
                                category = ", ".join([r for r in reasons if "✅" not in r]) or "Normal"

                                log_data = {
                                    "id": len(seen_files)*1000 + len(logs_data) + len(temp_logs),
                                    "file": filename,
                                    "timestamp": row[0] if len(row) > 0 else "",
                                    "source": row[2] if len(row) > 2 else "",
                                    "event": row[6] if len(row) > 6 else "",
                                    "severity": row[13] if len(row) > 13 else "",
                                    "alerts": reasons,
                                    "raw_reasons": reasons,
                                    "user_verified": None,
                                    "category": category
                                }
                                temp_logs.append(log_data)

                    # push logs into queue
                    for log in temp_logs:
                        log_queue.put(log)

                    # ✅ After fully reading the file, move it to processed folder
                    new_path = os.path.join(PROCESSED_FOLDER, filename)
                    try:
                        shutil.move(filepath, new_path)
                        print(f"Moved processed log: {filename} → {PROCESSED_FOLDER}")
                    except Exception as e:
                        print(f"Error moving file {filename}: {e}")

            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print("Error in monitor:", e)
            time.sleep(5)

# ===== FLASK APP =====
app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>SIEM Dashboard</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; background: #111; color: #eee; padding: 20px; }
        h1 { color: #00ff99; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #555; padding: 8px; }
        th { background: #222; }
        .alert { color: #ff4d4d; font-weight: bold; }
        .ok { color: #00ff99; font-weight: bold; }
        form { margin-top: 5px; }
        button { margin: 2px; padding: 4px 8px; border: none; border-radius: 4px; cursor: pointer; }
        .yes { background: #ff4d4d; color: white; }
        .no { background: #00cc66; color: white; }
    </style>
</head>
<body>
    <h1>🔍 Real-Time SIEM Log Dashboard</h1>
    <table>
        <tr>
            <th>File</th>
            <th>Timestamp</th>
            <th>Source</th>
            <th>Event</th>
            <th>Severity</th>
            <th>Analysis</th>
            <th>Category</th>
            <th>LLM Verification</th>
        </tr>
        {% for entry in logs %}
        <tr>
            <td>{{ entry.file }}</td>
            <td>{{ entry.timestamp }}</td>
            <td>{{ entry.source }}</td>
            <td>{{ entry.event }}</td>
            <td>{{ entry.severity }}</td>
            <td>
                {% for a in entry.alerts %}
                    <div class="{% if '✅' in a %}ok{% else %}alert{% endif %}">{{ a }}</div>
                {% endfor %}
            </td>
            <td>{{ entry.category }}</td>
            <td>
                {% if entry.user_verified == None and not ('✅' in entry.alerts[0]) %}
                    <form method="POST" action="/verify/{{ entry.id }}">
                        <button type="submit" name="answer" value="yes" class="yes">Yes</button>
                        <button type="submit" name="answer" value="no" class="no">No</button>
                    </form>
                {% elif entry.user_verified == True %}
                    ✅ Marked as anomaly by user
                {% elif entry.user_verified == False %}
                    ☑️ Marked as safe by user
                {% endif %}
            </td>
        </tr>
        {% else %}
        <tr><td colspan="8">No logs processed yet...</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

logs_data = []

@app.route("/")
def index():
    return render_template_string(html_template, logs=logs_data)

@app.route("/api/logs")
def api_logs():
    return jsonify(logs_data)

@app.route("/verify/<int:log_id>", methods=["POST"])
def verify(log_id):
    answer = request.form.get("answer")
    for entry in logs_data:
        if entry["id"] == log_id:
            if answer == "yes":
                # keep real reasons as category
                reasons = [r for r in entry.get("raw_reasons", []) if "✅" not in r]
                if not reasons:
                    reasons = ["🚨 User-flagged anomaly (manual flag)"]

                category = ", ".join(reasons)
                entry["alerts"] = [f"🚨 Marked as anomaly by user ({category})"]
                entry["user_verified"] = True
                entry["category"] = category

                # Save anomaly with full details
                with open(ANOMALY_FILE, "a", encoding="utf-8") as f:
                    f.write(
                        f"[File: {entry['file']}] "
                        f"[ID: {entry['id']}] "
                        f"[Category: {entry['category']}] "
                        f"[Timestamp: {entry['timestamp']}] "
                        f"[Event: {entry['event']}] "
                        f"→ {', '.join(entry['alerts'])}\n"
                    )

            else:
                entry["alerts"] = ["✅ No anomalies detected"]
                entry["user_verified"] = False
                entry["category"] = "Normal"
            break
    return redirect(url_for("index"))


def process_queue():
    while True:
        try:
            entry = log_queue.get()
            logs_data.insert(0, entry)
            if len(logs_data) > 50:
                logs_data.pop()
        except:
            pass
        time.sleep(1)

# ===== START SERVER =====
if __name__ == "__main__":
    os.makedirs(LOG_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    threading.Thread(target=monitor_logs, daemon=True).start()
    threading.Thread(target=process_queue, daemon=True).start()

    print("🚀 SIEM Dashboard running at http://127.0.0.1:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
