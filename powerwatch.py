
import time
import random

# Simulated statuses (in a real setup, these would come from sensors or inverter API)
power_sources = {
    "solar": True,
    "battery_level": 85,   # Percent
    "generator": False,
    "grid": False
}

LOG_FILE = "powerwatch_log.txt"

def log_event(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.ctime()} - {message}\n")

def send_alert(subject, message):
    print(f"📡 ALERT: {subject}\n{message}")
    log_event(f"{subject} - {message}")

def enforce_power_priority():
    # Step 1: Solar must be primary
    if power_sources["solar"] and power_sources["battery_level"] > 30:
        log_event("✅ Solar active – system running on primary power.")
        return

    # Step 2: If solar low, switch to generator
    if power_sources["battery_level"] <= 30 and not power_sources["generator"]:
        power_sources["generator"] = True
        send_alert("⚠️ Battery Low", "Switching to generator as solar battery is below threshold.")
        return

    # Step 3: Grid is last resort
    if not power_sources["solar"] and not power_sources["generator"] and not power_sources["grid"]:
        power_sources["grid"] = True
        send_alert("🟥 Emergency Fallback", "Solar and generator unavailable – switching to grid (last resort).")
        return

    if power_sources["grid"] and (power_sources["solar"] or power_sources["generator"]):
        send_alert("🚨 Unauthorized Grid Use", "Grid power active while solar/generator are operational.")
        return

def simulate_runtime_check():
    for _ in range(5):
        enforce_power_priority()
        # Simulate minor changes (in real use, update this from sensors or logs)
        power_sources["battery_level"] -= random.randint(5, 10)
        time.sleep(2)

if __name__ == "__main__":
    simulate_runtime_check()
