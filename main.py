
import threading

# Existing core modules
import siemcore
import patternengine
import threatdna
import flowtrap
import casewatch
import pluginloader
import stealthcam
import phantomstaff
import lockdown
import quarantine
import mailwatch
import resurgwatch
import honeypot
import patchcheck_v2

# New upgraded modules
import behaviorwatch
import clamwatch
import edrwatch
import forensicswatch
import assetwatch

def run_all():
    modules = [
        siemcore, patternengine, threatdna, flowtrap, casewatch, pluginloader,
        stealthcam, phantomstaff, lockdown, quarantine, mailwatch, resurgwatch,
        honeypot, patchcheck_v2, behaviorwatch, clamwatch, edrwatch,
        forensicswatch, assetwatch
    ]
    for module in modules:
        try:
            threading.Thread(target=module.run, daemon=True).start()
        except Exception as e:
            with open("error_log.txt", "a") as f:
                f.write(f"Error in {module.__name__}: {str(e)}\n")

if __name__ == "__main__":
    run_all()
