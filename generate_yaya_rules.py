#!/usr/bin/env python3
"""
SentinelIT — Generate default YARA rules for memorywatch.py
Creates 10 sample YARA rules covering LOLBins, PowerShell, Python, Office macros,
ransomware patterns, network trojans, scripts, Linux malware, and memory injections.
"""

import os
from pathlib import Path

# Folder where YARA rules will be saved
RULES_DIR = Path("./yara_rules")
RULES_DIR.mkdir(parents=True, exist_ok=True)

# Dictionary of filename -> rule content
yara_rules = {
    "lolbins.yar": """
rule LOLBins
{
    meta:
        author = "SentinelIT"
        description = "Detects execution of known LOLBins"

    strings:
        $rundll32 = "rundll32.exe" nocase
        $mshta    = "mshta.exe" nocase
        $certutil = "certutil.exe" nocase
        $regsvr32 = "regsvr32.exe" nocase

    condition:
        any of ($*)
}
""",
    "powershell_injection.yar": """
rule PowershellInjection
{
    meta:
        author = "SentinelIT"
        description = "Detects potentially malicious PowerShell usage"

    strings:
        $enc      = "-enc" ascii
        $iex      = "Invoke-Expression" ascii
        $bypass   = "-ExecutionPolicy Bypass" ascii

    condition:
        any of ($*)
}
""",
    "python_suspicious.yar": """
rule SuspiciousPython
{
    meta:
        author = "SentinelIT"
        description = "Detects suspicious Python scripts"

    strings:
        $exec_eval = "exec(" ascii
        $eval      = "eval(" ascii
        $base64    = "base64" ascii

    condition:
        any of ($*)
}
""",
    "memory_injection.yar": """
rule AnonymousExecMemory
{
    meta:
        author = "SentinelIT"
        description = "Detects anonymous memory regions with execute permissions"

    strings:
        $anonx = "<anonymous>" ascii
        $anonx2 = "[anon" ascii

    condition:
        any of ($*)
}
""",
    "macro_malware.yar": """
rule OfficeMacroMalware
{
    meta:
        author = "SentinelIT"
        description = "Detects embedded macro keywords in Office files"

    strings:
        $vba = "VBA" ascii
        $autoopen = "AutoOpen" ascii
        $shell = "Shell" ascii

    condition:
        any of ($*)
}
""",
    "ransomware_patterns.yar": """
rule RansomwarePatterns
{
    meta:
        author = "SentinelIT"
        description = "Detects common ransomware file operation strings"

    strings:
        $encfile = ".encrypted" ascii
        $extlock = ".locked" ascii
        $readme  = "README_FOR_DECRYPT" ascii

    condition:
        any of ($*)
}
""",
    "network_trojan.yar": """
rule NetworkTrojan
{
    meta:
        author = "SentinelIT"
        description = "Detects network trojans and backdoors"

    strings:
        $connect = "connect" ascii
        $cmdsock = "cmd.exe" ascii
        $netcat  = "nc.exe" nocase

    condition:
        any of ($*)
}
""",
    "suspicious_scripts.yar": """
rule SuspiciousScripts
{
    meta:
        author = "SentinelIT"
        description = "Detects suspicious scripting patterns"

    strings:
        $javascript = "<script>" ascii
        $wscript    = "WScript.Shell" ascii
        $eval_js    = "eval(" ascii

    condition:
        any of ($*)
}
""",
    "linux_malware.yar": """
rule LinuxMalware
{
    meta:
        author = "SentinelIT"
        description = "Detects common Linux malware indicators"

    strings:
        $binbash  = "/bin/bash" ascii
        $wget     = "wget " ascii
        $curl     = "curl " ascii
        $chmod    = "chmod" ascii

    condition:
        any of ($*)
}
""",
    "memorywatch_alerts.yar": """
rule MemoryWatchAlerts
{
    meta:
        author = "SentinelIT"
        description = "Detects high-memory process anomalies or injections"

    strings:
        $rwxmem = "RWX" ascii
        $anon   = "<anonymous>" ascii
        $susp   = "suspicious" ascii

    condition:
        any of ($*)
}
"""
}

# Write each rule to file
for fname, content in yara_rules.items():
    out_path = RULES_DIR / fname
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[+] Created {out_path}")

print(f"\nAll {len(yara_rules)} YARA rules generated in {RULES_DIR.resolve()}")
