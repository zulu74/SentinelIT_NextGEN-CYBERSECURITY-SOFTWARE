
import os
from datetime import datetime

def generate_report(data, output_dir="reports"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"sentinel_report_{timestamp}.txt"
    report_path = os.path.join(output_dir, report_filename)

    with open(report_path, "w") as report_file:
        report_file.write("SentinelIT Risk Intelligence Report\n")
        report_file.write("="*50 + "\n")
        for key, value in data.items():
            report_file.write(f"{key}: {value}\n")

    print(f"[+] Report generated at: {report_path}")
    return report_path

# Entry point function for autoexec
def run_reportgen():
    # Sample data structure to demonstrate report generation
    test_data = {
        "Scan Status": "Completed",
        "Threats Detected": 2,
        "Quarantined Files": 1,
        "System Integrity": "Stable"
    }
    generate_report(test_data)
