
import psutil

# List of common reverse engineering tool process names
RE_TOOL_NAMES = [
    "ghidra", "ida", "idag", "idaw", "ida64", "ida32",
    "cutter", "radare2", "x64dbg", "x32dbg", "ollydbg",
    "dnspy", "de4dot", "binaryninja", "windbg"
]

def detect_reverse_tools():
    for proc in psutil.process_iter(['name']):
        try:
            pname = proc.info['name'].lower()
            if any(tool in pname for tool in RE_TOOL_NAMES):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False
