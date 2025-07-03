
import os
import datetime
import shutil

class ReportManager:
    def __init__(self, report_dir="SentinelReports"):
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    def save_report(self, report_data, filename=None):
        if not filename:
            filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(self.report_dir, filename)
        with open(file_path, 'w') as f:
            f.write(report_data)
        print(f"[+] Report saved to {file_path}")
        return file_path

    def list_reports(self):
        return [f for f in os.listdir(self.report_dir) if os.path.isfile(os.path.join(self.report_dir, f))]

    def delete_report(self, filename):
        path = os.path.join(self.report_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            print(f"[-] Deleted report: {filename}")
        else:
            print("[!] Report not found.")

    def archive_reports(self, archive_name="ArchivedReports.zip"):
        archive_path = shutil.make_archive(archive_name.replace(".zip", ""), 'zip', self.report_dir)
        print(f"[+] Archived reports to {archive_path}")
        return archive_path
