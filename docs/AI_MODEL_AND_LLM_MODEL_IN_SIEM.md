AI MODEL AND LLM MODEL IN SIEM

INTRODUCTION:

In our SIEM system, the primary goal is to process a massive volume of log data generated daily by more number of systems, identify problematic records (e.g., virus attacks, spam, unauthorized access), and provide intelligent analysis. This is where two important components come in: 

1. AI MODEL – for anomaly detection and pre-classification
2. LLM MODEL – for natural language understanding, classification validation, and solution suggestion

----------------------------
PART 1: WORK OF THE AI MODEL
----------------------------

The AI model acts as a pre-filtering mechanism before logs are passed to the LLM. It uses machine learning techniques to detect unusual behavior or patterns in the log entries.

Key steps:

1. DATA PREPROCESSING:
   - All daily log entries from client systems are cleaned and structured.
   - Important features (e.g., user ID, timestamp, IP address, event type, access type, file status) are extracted.

2. FEATURE ENGINEERING:
   - AI model calculates derived metrics like:
     * Frequency of login failures
     * Number of emails received per hour
     * Number of access requests per day
   - Converts raw logs into numerical vectors for training.

3. ANOMALY DETECTION:
   - Models like Isolation Forest, Autoencoder, or One-Class SVM are used.
   - These models learn the "normal behavior" from historical logs.
   - Anything that deviates significantly from this behavior is marked as "anomalous" or "suspicious".

4. PROBLEMATIC LOG IDENTIFICATION:
   - The AI model tags logs with labels such as:
     * Suspicious login
     * Spam mail
     * Virus file
     * Unknown application behavior

5. REDUCE FALSE ALERTS:
   - AI model filters out most obvious normal entries and reduces the workload for the LLM by only forwarding the "uncertain or suspicious" logs.

----------------------------
PART 2: WORK OF THE LLM MODEL
----------------------------

Once the AI model identifies potentially problematic log entries or files, they are passed to the LLM (Large Language Model) for deeper understanding and decision-making in natural language.

Key steps:

1. LOG INTERPRETATION:
   - The LLM receives a log entry and a prompt like:
     "Analyze this log and tell if it indicates a real problem or not."
   - Example input:
     "User xyz logged in from IP 192.168.2.5 in India at 12:00 PM, and from IP 10.25.17.3 in Germany at 12:03 PM."
   - The LLM understands the context and checks for possible compromise.

2. CLASSIFICATION DECISION:
   - The LLM acts as an intelligent validator.
   - It confirms whether the log is a true positive, false positive, true negative, or false negative.
   - For example, a virus warning that seems real but triggered by a harmless file may be classified as a false positive.

3. EXPLANATION GENERATION:
   - The LLM generates a human-readable explanation of the issue.
   - Example:
     "The login from two geographically distant IPs in a short time is abnormal and suggests a possible account compromise."

4. SUGGESTION OF ACTIONS:
   - Based on log type, the LLM also recommends actions:
     * "Block the IP address immediately."
     * "Notify the user and force a password reset."
     * "Mark this log as harmless. No action needed."

5. HANDLING DIFFERENT FILE FORMATS:
   - When a problematic file (CSV/Excel) is detected by the watcher system, the LLM can also read the file content (after parsing via pandas or similar tools) and explain:
     * If the format is incorrect
     * If the data inside suggests abnormal activity

---------------------------------------
FINAL GOAL OF AI + LLM INTEGRATION:
---------------------------------------
- AI Model quickly filters large log data and detects suspicious patterns.
- LLM Model intelligently interprets those logs and makes clear, reliable decisions.
- This combined system reduces manual work for security teams, minimizes false alerts, and improves the speed and accuracy of threat detection in our SIEM system.
