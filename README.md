# 🛡️ SentinelIT – NextGEN Cybersecurity Suite
**Powered by AI • Hardened by Design • Unmatched in Defense**

SentinelIT is an advanced AI-driven cybersecurity system engineered to detect, defend, and neutralize modern cyber threats in real-time. Designed for governments, enterprises, and high-risk sectors, SentinelIT integrates cutting-edge protection, zero-day response, deception technologies, and multi-executive access control in one powerful framework.

---

## 🔥 What’s New (2025 Edition)

### ✅ Core Enhancements:
- **Modularized System Launch**: Central `ultimate_main.py` runs all modules simultaneously.
- **New Vault Security**: `vaultwatch.py` – Requires 6 unique passcodes to access critical data, with timed lockout and Code Red triggers.
- **Power Resilience**: `powerwatch.py` monitors power conditions with triple-source backup logic (solar, generator, grid).
- **Dynamic Obfuscation**: Location shifts between 20,000+ randomized global proxies every 5 seconds.

---

## ⚙️ Modules Overview (50+ modules, and growing)

| Module             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `usbwatch.py`      | Detects and logs USB insertions, runs behavioral threat scan automatically. |
| `phantomstaff.py`  | AI-driven IT helpdesk for front-line response and silent system defense.     |
| `vaultwatch.py`    | Multi-passcode vault access, triggers full shutdown on unauthorized access.  |
| `stealthcam.py`    | Captures webcam images when suspicious commands are executed.                |
| `lockdown.py`      | Locks CMD/PowerShell on unauthorized users and logs all access attempts.     |
| `quarantine.py`    | Automatically isolates files or devices showing threat behavior.             |
| `mailwatch.py`     | Scans clipboard and emails for malicious links or phishing redirectors.      |
| `patchcheckv2.py`  | Detects outdated apps, cross-references CVEs, and auto-generates fix reports.|
| `resurgwatch.py`   | AI detects re-emerging CVEs masked under modified logic.                     |
| `traveltrap_email.py` | Detects phishing via URL redirect traps like Google /travel/clk.         |
| `pluginloader.py`  | Dynamically loads and monitors module status and integrity.                  |
| `threatdna.py`     | Profiles malware signatures using historical CVE patterns.                   |
| `patternengine.py` | Detects behavioral anomalies using logic pattern analytics.                  |
| `siemcore.py`      | Core AI-enhanced SIEM for live monitoring, logging, and alerting.            |
| `memorywatch.py`   | Monitors system memory for injection or buffer overflow attempts.            |
| `kernelwatch.py`   | Detects tampering at kernel level with live response logic.                  |
| `dashboard_server.py` | Hosts a secure local dashboard for all AI logs and reports.              |
| `trayiconrunner.py`| Background runner that shows a system tray icon confirming SentinelIT is live.|
| `recoguard.py`     | Monitors reconnaissance techniques and logs any enumeration attempts.        |
| `kalitrap.py`      | Detects and deflects attacks from popular Kali Linux tools.                  |
| `iotmonitor.py`    | Monitors IoT traffic, detects spoofing or unauthorized device changes.       |

---

## 🔐 Unmatched Security Features

- **AI Helpdesk Automation** – Users receive real-time support, password resets, and lockdowns via PhantomStaff.
- **Triple OTP Admin Lockdown** – No admin/root access unless approved by 3 executives in real-time.
- **Real-time Threat Response** – Instant quarantine, alerting, and deception on suspected attacks.
- **Reconnaissance & Enumeration Detection** – Blocks and logs active scans and Nmap attempts.
- **CVE Watchlist with Weekly Reports** – Tracks CVE-2024/2025 and critical infrastructure threats.
- **Zero Human Window Exploits** – No 5-second exploit windows for admins. Full system surveillance is enforced.
- **Redundancy Design** – Solar → Generator → Grid power logic. Electricity is the last resort.
- **Auto Update & Audit** – Weekly self-audits with full PDF reports, CVSS scoring, and fix recommendations.

---

## 🧠 Ideal For:
- Government & Military Defense
- Telecom & Financial Institutions
- Infrastructure & Energy Sectors
- Private Security Firms
- Red/Blue Teams

---

## 🧪 Testing Environment

For live penetration test simulation:
```bash
# Termux/Kali test
nmap -A 192.168.0.X
python ultimate_main.py