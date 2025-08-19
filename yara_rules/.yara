// ----------------------------------------------------
// SentinelIT Combined YARA Rules for MemoryWatch
// Contains: LOLBins, Office Macros, PowerShell, Injection, Scripts
// ----------------------------------------------------

// --- 1. LOLBin detection ---
rule lolbin_detection
{
    meta:
        description = "Detects common LOLBins (rundll32, mshta, regsvr32, certutil)"
    strings:
        $rundll32 = "rundll32.exe"
        $mshta = "mshta.exe"
        $regsvr32 = "regsvr32.exe"
        $certutil = "certutil.exe"
    condition:
        any of ($rundll32, $mshta, $regsvr32, $certutil)
}

// --- 2. Suspicious Office macros ---
rule office_macro_suspicious
{
    meta:
        description = "Detects suspicious Office macros"
    strings:
        $macro1 = /AutoOpen/i
        $macro2 = /Document_Open/i
        $macro3 = /ShellExecute/i
    condition:
        any of ($macro*)
}

// --- 3. PowerShell script indicators ---
rule powershell_suspicious
{
    meta:
        description = "Detects suspicious PowerShell commands"
    strings:
        $exec = /Invoke-Expression/i
        $bypass = /-ExecutionPolicy Bypass/i
        $download = /DownloadString/i
    condition:
        any of ($exec, $bypass, $download)
}

// --- 4. Suspicious executable injection ---
rule exe_injection
{
    meta:
        description = "Detects suspicious EXE or memory injection patterns"
    strings:
        $anon = /<anonymous>/i
        $rwx = /RWX/i
    condition:
        any of ($anon, $rwx)
}

// --- 5. Generic suspicious scripts ---
rule suspicious_scripts
{
    meta:
        description = "Detects suspicious scripts or batch commands"
    strings:
        $cmd = /cmd\.exe/i
        $vbs = /\.vbs/i
        $js = /\.js/i
    condition:
        any of ($cmd, $vbs, $js)
}
