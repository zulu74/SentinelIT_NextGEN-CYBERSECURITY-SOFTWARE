# SentinelIT\_Build

**SentinelIT** is a next-generation modular security suite designed to deliver real-time protection, compliance monitoring, and self-healing capabilities. Built with enterprise-level architecture, SentinelIT combines AI-enhanced defense mechanisms with deep system integration for unmatched resilience.

---

## 🚀 Key Features

### 🧠 Core Architecture

* Modular engine with dynamic threading for each defense layer
* Full background operation with system tray interface
* Auto-healing via `selfmaintainer.py`

### 📊 Live Dashboard

* `sentinelitgui.py` provides a redesigned tabbed interface with:

  * Dashboard (status overview)
  * Modules control panel
  * Real-time log viewer
  * Settings for triggering compliance and health checks

### 🔐 Security Modules

* `usbwatch.py`: Real-time USB scanning, triple OTP quarantine, behavioral analysis
* `phantomstaff.py`: AI voice-integrated security assistant
* `stealthcam.py`: Silent webcam activity monitor
* `lockdown.py`: System lockdown on breach
* `quarantine.py`: Isolates flagged files/drives automatically
* `patchcheckv2.py`: Patch audit and CVE reporting
* `siemcore.py`: AI-powered SIEM with correlation engine
* `kernelwatch.py` / `memorywatch.py`: Kernel and memory integrity monitors
* `threatdna.py`: Behavioral fingerprint engine for detecting injected threats

### 📦 Network & Protocol Defense

* `ftpwatch.py`: FTP access control with secondary authentication
* `snmpguard.py`: SNMP monitor with secure access gate
* `traveltrap_email.py`: Location-aware email trap for data exfiltration
* `iotmonitor.py`: IoT port scan and anomaly detection
* `mailwatch.py`: Email activity scanner

### 🧠 AI & Behavior

* `resurgwatch.py`: Resurrection trap monitor
* `powerwatch.py`: Power event auditing
* `patternengine.py`: Pattern anomaly learner
* `pluginloader.py`: Dynamic AI plug-in injection system

### 🛡️ Compliance & Audit

* `schedule.py`: Automated compliance scanning scheduler
* `compliance_monitor.py`: Live SOC 2 auditing engine
* `Eventlogger.py`: Unified logging framework with event tagging
* `license_tracker.py`: Track license use and expiry
* `integrate_activation.py`: Module registration gateway
* `report_manager.py`: Generates weekly vulnerability and audit reports

### 🌐 Web & Remote Interface

* `dashboard_server.py`: Localhost Flask interface for dashboard display
* `trayiconrunner.py`: Background notifier with alerts and exit control

---

## ✅ Self-Healing System

* `selfmaintainer.py`: Performs system repairs, module validation, and stealth patching every 6 hours
* Launch check + background update loop

---

## 🔧 Getting Started

```bash
python ultimate_main.py
```

This launches all modules via multi-threaded orchestration.

---

## 📁 Folder Structure

```
SentinelIT_Build/
├── sentinelitgui.py
├── ultimate_main.py
├── selfmaintainer.py
├── ftpwatch.py
├── snmpguard.py
├── patchcheckv2.py
├── Eventlogger.py
├── [All other modules...]
└── README.md
```

---

## 🏁 How to Contribute

Pull requests and ideas are welcome. This project is built to be expanded for enterprise, educational, or SOC-level defense scenarios.

---

## 🧠 Vision

SentinelIT aims to be the **most modular, AI-integrated, and defensive cyber framework** for proactive systems security — from the USB port to the cloud.

> “Not just secure. Untouchable.”

---

© 2025 SentinelIT | Built by Zulu
