# SentinelIT 🛡️

**AI-Powered Cybersecurity Suite for Resource-Constrained Environments**

SentinelIT is a next-generation cybersecurity system built for speed, resilience, and intelligent protection. Designed to thrive in resource-limited environments across Africa, it offers real-time threat detection, self-healing, offline-first architecture, and AI-assisted defense for decentralized, low-power machines.

---

## 🚀 Key Features

- **Modular Architecture** — Each function runs independently (USB scanning, memory watch, network inspection, CVE checks, etc.)
- **Self-Healing** — Auto-recovers modules and maintains system integrity via `selfmaintainer.py`
- **Offline Capabilities** — No reliance on cloud; each node (branch computer) performs its own threat detection
- **AI-Enhanced Detection** — Uses behavioral patterns and attack fingerprints to detect advanced threats
- **Live Dashboard** — Real-time system stats and multi-node visibility via `app.py`
- **Multi-Node Monitoring** — Branch-based or device-based threat reporting (e.g., `Computer-1`, `Computer-2`, up to `Computer-1000`)
- **Port & Protocol Enforcement** — Includes watchdogs for FTP, SNMP, and lockdown enforcement
- **Customizable Threat Reporting** — Categorized by severity: High, Medium, Low
- **PhantomStaff Integration** — Embedded voice + AI assistant for system responses
- **Tray Icon Runner** — Light system tray presence for user visibility
- **Encrypted Audit & SOC2 Support** — Adds continuous compliance audit logging and CVE tracking

---

## 🔧 Technologies Used

- **Languages:** Python 3.11+
- **Frameworks:** Flask, Flask-SocketIO, SQLAlchemy, Flask-Login
- **Databases:** SQLite (default)
- **System Monitoring:** psutil
- **UI:** HTML/CSS (with Socket.IO updates)
- **Security Modules:** Custom modules (siemcore, threatdna, quarantine, lockdown, patchcheckv2, etc.)

---

## 🌍 Why It Matters

SentinelIT was created for **Africa Deep Tech Challenge 2025** to demonstrate that powerful, intelligent cybersecurity is achievable even without high-end servers or unlimited internet. SentinelIT proves that national-grade defense is possible in:

- Rural clinics and schools
- Municipal branches
- Field offices and mobile laptops
- Power-interrupted or air-gapped networks

---

## 🧪 Modules List (Partial)

- `phantomstaff.py` — AI security assistant
- `threatdna.py` — Threat pattern intelligence
- `usbwatch.py` — Malicious USB and payload detection
- `patchcheckv2.py` — System vulnerability audit + CVE
- `dashboard_server.py` — Live metrics dashboard
- `lockdown.py` — CMD/policy lock enforcement
- `memorywatch.py`, `kernelwatch.py`, `powerwatch.py`, etc.
- `app.py` — Main Flask app with user login + multi-node dashboard
- `selfmaintainer.py` — Healing and auto-repair system

---

## 🧠 Inspired By

Built for the **Bolt Hackathon** and **Africa Deep Tech Challenge**, SentinelIT was inspired by the challenges in securing decentralized, low-resourced offices in Africa. We saw a gap in enterprise-level protection for remote, offline, or underpowered systems—and we filled it.

---

## 🛠️ How to Run

```bash
# Clone
$ git clone https://github.com/yourusername/SentinelIT_Build.git
$ cd SentinelIT_Build

# Install dependencies (create a venv recommended)
$ pip install -r requirements.txt

# Launch full system
$ python ultimate_main.py

# Launch dashboard (in another terminal)
$ python app.py
```

---

## ✅ Admin Credentials
Default login after setup:
- **Email:** admin@sentinel.com
- **Password:** admin123

---

## 🧩 License
This software is provided for ethical and educational use. For enterprise usage or partnership, contact the creator.

---

> Built with ❤️ by Zulu
