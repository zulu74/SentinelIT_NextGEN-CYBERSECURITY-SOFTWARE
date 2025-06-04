🛡️ SentinelIT – AI-Driven Cyber Defense Suite

SentinelIT is a next-generation cybersecurity defense system built to detect, prevent, and respond to modern cyber threats using real-time analytics, AI automation, and enterprise-grade protection modules.

🔍 Key Features

🔐 Security & Detection

ScanTrap – Detects active reconnaissance (Nmap, Unicorn, ZMap)

BannerTrap – Identifies unauthorized banner grabbing attempts

DNSWatch – Detects spoofing, tunneling, and DNS anomalies

XSSWatch – Stops blind, reflected, and stored XSS injections

TravelTrap – Traps phishing redirect attacks (e.g. Google /travel/clk)

PatchEngine – Offline CVE scanner and patching guide

PolicyEngine – Security policy compliance enforcer


🧠 AI & Automation

AI Helpdesk (GUI + CLI) – Resolves login issues, automates password resets (Active Directory-aware)

ThreatDNA – Malware behavior and signature correlation

PatternEngine – Analyzes behavioral anomalies and attack patterns

FlowTrap & HoneyPing – Deploys honeypots and network deception

CaseWatch – Incident monitoring and escalation engine


📊 Interface & Reports

Custom GUI Dashboard – Shield watermark, watermark branding, visual threat status

PDF Reporting – Auto-generated SentinelIT Risk Intelligence Reports

Email Alerts – For phishing, login failures, policy violations


🏗️ Architecture

SentinelIT is modular and includes over 20 Python scripts that communicate through a central orchestrator (main.py). The system is designed for:

Windows and Linux environments

Corporate networks and hybrid cloud setups

OT/ICS protection support


💡 Innovation Highlights

Triple OTP security (executive approval-based remote access)

AI-powered IT front desk automation (via ID + name match)

GUI with stylized branding and auto-start support

Stealth traps for common hacking tools


🛠 Technologies Used

Purpose	Tools / Libraries

GUI	tkinter, Pillow
PDF Reports	fpdf
Email/Phishing Alerts	smtplib, ssl, email.mime
DNS & Network Traps	socket, scapy, dnspython
AD Password Reset	subprocess, pywin32 (Windows)
Logging & Parsing	json, os, datetime, platform
AI Pattern Detection	Custom logic, regex, entropy


🚀 How to Run

python main.py

To run specific modules:

python aihelpdesk_gui.py  # For GUI helpdesk interface
python reportgen.py        # To generate SentinelIT Risk Intelligence PDF

> ⚠️ Requires Python 3.11+ and appropriate OS-level permissions




---

🧪 Demo Video (Optional)

📺 [Upload or link here – e.g. YouTube or Loom]

🧑‍💻 Created By

James Zulu – System Engineer & Infrastructure Lead
💼 https://diakriszuluinvestmentsprojects.co.za
📧 james.zulu@diakriszuluinvestmentsprojects.co.za

🔒 License

This is a confidential proprietary solution under the Diakris Zulu Cyberdefense umbrella. Unauthorized use, distribution, or reproduction is strictly prohibited.


---

SentinelIT – Because tomorrow’s attacks need today’s intelligence.

