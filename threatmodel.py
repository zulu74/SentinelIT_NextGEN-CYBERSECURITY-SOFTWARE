import traveltrap

SentinelIT Phase 6 Main Controller

import siemcore import patternengine import threatdna import flowtrap import casewatch import pluginloader

=== Phase 7 OT/ICS Modules ===

from assetmap import run_assetmap from vulnscan import run_vulnscan from riskscore import run_riskscore from netviz import run_netviz from otwatch import run_otwatch from threatmodel import run_threatmodel

def run_all(): print("\n[START] Redirect Phishing Trap (Google /travel/clk)") traveltrap.run() print("[DONE] Redirect Phishing Trap\n")

print("[SentinelIT] Launching Phase 6 unified system...")
siemcore.run()
patternengine.run()
threatdna.run()
flowtrap.run()
casewatch.run()
pluginloader.run()

print("[+] Running Phase 7 Modules...")
run_assetmap()
run_vulnscan()
run_riskscore()
run_netviz()
run_otwatch()
run_threatmodel()

if name == "main": run_all()
