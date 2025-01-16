import json
import os
from datetime import datetime


class ResultsHandler:
    def __init__(self):
        self.results = {
            "registration": {"successful": 0, "failed": 0, "times": []},
            "login": {"successful": 0, "failed": 0, "times": []}
        }

    def update_results(self, operation, success, response_time):
        if success:
            self.results[operation]["successful"] += 1
        else:
            self.results[operation]["failed"] += 1
        self.results[operation]["times"].append(response_time)

    def generate_report(self, config):
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_configuration": {
                "concurrent_users": config.CONCURRENT_USERS,
                "total_iterations": config.ITERATIONS
            }
        }

        for operation in ["registration", "login"]:
            total = self.results[operation]["successful"] + self.results[operation]["failed"]
            avg_time = sum(self.results[operation]["times"]) / len(self.results[operation]["times"]) if \
            self.results[operation]["times"] else 0

            report[f"{operation}_results"] = {
                "successful": self.results[operation]["successful"],
                "failed": self.results[operation]["failed"],
                "average_response_time": f"{avg_time:.3f} seconds",
                "success_rate": f"{(self.results[operation]['successful'] / total * 100):.2f}%" if total > 0 else "0%"
            }

        report_path = os.path.join("reports", f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs("reports", exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)

        return report
