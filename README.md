
# SentinelIT

**Powered AI. Hardened Systems. Zero Compromise.***

SentinelIT is a fully autonomous cybersecurity defense system designed to secure enterprise and endpoint environments through advanced detection, prevention, and AI-driven remediation.

---

## 🧠 Core Features

- ✅ AI-Powered Threat Detection & Response
- 🔐 Triple-OTP Remote Access Control
- 📷 StealthCam: Silent Camera Activation on Suspicious Events
- 🧬 PatternEngine: Behavior-Based Exploit Detection
- 🔒 CMD & PowerShell Lockdown + Logging (Now Adaptive)
- 🛡️ Hardened Startup Tray Monitor (`sentinelit_monitor.py`)
- 📈 AI Speed Optimizer + System Health Monitor (`ai_speed_monitor.py`)
- ☁️ Cloud Activity Hooks (`cloudwatch.py`)
- ⚠️ WebDAV 0-Day (CVE-2025-33053) Exploit Protection (`webdavwatch.py`)
- 🖼️ Visual Splash Startup (`splash_screen.py`)
- 📦 Ultimate Launcher (`ultimate_main.py`) – boots all modules in parallel
- 🧠 PhantomStaff: AI Assistant + USB Authorization + Duress Traps

---

## 🔧 Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/zulu74/SentinelIT.git
   cd SentinelIT
   ```

2. Optional: Activate virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the main launcher:
   ```bash
   python ultimate_main.py
   ```

---

## ⚙️ Auto-Startup Tray Icon

- `sentinelit_monitor.py` runs from system tray and boots core modules
- Autostarts on Windows login

---

## 🛑 Active Threat Mitigations

- CVE-2025-33053 (WebDAV RCE) – Fully disabled WebClient + monitored connections
- USB Threat Scanning (via `usbwatch.py`)
- Stealth Camera, Logging, and Lockdown triggers

---

## 📷 Splash Screen

- Static image (`SentinelIT_Startup.png`) shows for 3 seconds at startup

---

## 👤 Author

**James Zulu**  
GitHub: [https://github.com/zulu74](https://github.com/zulu74)  
LinkedIn: [https://www.linkedin.com/in/jameszulu](https://www.linkedin.com/in/jameszulu)

---

## ❗ Legal

For ethical use only. Do not deploy SentinelIT in unauthorized environments.
