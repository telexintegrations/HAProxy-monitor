import subprocess
import csv
from datetime import datetime
import requests
import io


class HAProxyMonitor:
    def __init__(self, telex_webhook_url, stats_endpoint, username=None, password=None):
        self.telex_webhook_url = telex_webhook_url
        self.stats_endpoint = stats_endpoint
        self.username = username
        self.password = password

    def get_haproxy_stats(self):
        """Collect HAProxy statistics"""
        try:
            auth = None
            if self.username and self.password:
                auth = (self.username, self.password)

            response = requests.get(
                self.stats_endpoint,
                auth=auth,
                verify=False,  # Only if needed for self-signed certs
            )
            return response.text
        except Exception as e:
            return f"Error collecting stats: {str(e)}"

    def parse_stats(self, stats_output):
        """Parse HAProxy stats into meaningful metrics"""
        metrics = {
            "backends": [],
            "total_requests": 0,
            "total_errors": 0,
            "error_breakdown": {
                "connection_errors": 0,
                "response_errors": 0,
                "request_errors": 0,
            },
        }

        # Parse CSV-like output
        f = io.StringIO(stats_output)
        csv_reader = csv.DictReader(f, delimiter=",")

        for row in csv_reader:
            if row["svname"] not in ["FRONTEND", "BACKEND"]:
                backend_metrics = {
                    "name": row.get("svname", "unknown"),
                    "status": row.get("status", "unknown"),
                    "total_sessions": int(row.get("stot", 0) or 0),
                    "last_status_change": f"{int(row.get('lastchg', 0) or 0) // 3600}h {(int(row.get('lastchg', 0) or 0) % 3600) // 60}m",
                    "failed_checks": int(row.get("chkfail", 0) or 0),
                    "current_queue": int(row.get("qcur", 0) or 0),
                    "max_queue": int(row.get("qmax", 0) or 0),
                    "response_time": int(row.get("rtime", 0) or 0),
                }
                metrics["backends"].append(backend_metrics)

            # Accumulate error counts
            metrics["error_breakdown"]["connection_errors"] += int(
                row.get("econ", 0) or 0
            )
            metrics["error_breakdown"]["response_errors"] += int(
                row.get("eresp", 0) or 0
            )
            metrics["error_breakdown"]["request_errors"] += int(row.get("ereq", 0) or 0)

        metrics["total_errors"] = sum(metrics["error_breakdown"].values())
        return metrics

    def format_daily_report(self, metrics):
        """Format metrics into a daily report"""
        report = [
            "🔍 HAProxy Health Report",
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        ]

        # Backend Status
        report.append("📊 Backend Servers Status:")
        for backend in metrics["backends"]:
            status_emoji = "✅" if backend["status"] == "UP" else "❌"
            report.append(
                f"{status_emoji} {backend['name']}:\n"
                f"  • Status: {backend['status']}\n"
                f"  • Sessions handled: {backend['total_sessions']}\n"
                f"  • Up time: {backend['last_status_change']}\n"
                f"  • Failed checks: {backend['failed_checks']}\n"
                f"  • Response time: {backend['response_time']}ms"
            )

        report.append("\n🚨 Error Summary:")
        report.append(f"Total Errors: {metrics['total_errors']}")
        for error_type, count in metrics["error_breakdown"].items():
            report.append(f"  • {error_type.replace('_', ' ').title()}: {count}")

        return "\n".join(report)

    def send_to_telex(self, message):
        """Send report to Telex channel"""
        try:
            payload = {
                "username": "HAProxy Monitor",
                "event_name": "HAProxy Monitor",
                "message": message,
                "status": "success",
            }

            response = requests.post(
                self.telex_webhook_url,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            print(response.json())
            return response.status_code
        except Exception as e:
            print(f"Error sending to Telex: {str(e)}")
            return False

    def run_check(self):
        """Execute daily monitoring check"""
        stats_output = self.get_haproxy_stats()
        print("stats_output", stats_output)
        metrics = self.parse_stats(stats_output)
        report = self.format_daily_report(metrics)
        return self.send_to_telex(report)


def main():
    monitor = HAProxyMonitor(
        telex_webhook_url="https://ping.telex.im/v1/webhooks/01951385-f313-7195-83f1-0ebf19ff972a",
        stats_endpoint="http://localhost/haproxy-status",
    )
    monitor.run_check()


if __name__ == "__main__":
    main()
