import subprocess

def run_behave_tests():
    """Run Behave tests."""
    result = subprocess.run(["behave"], capture_output=True, text=True)
    print("Behave Output:\n", result.stdout)
    print("Behave Error:\n", result.stderr)  # Print stderr for detailed error messages
    if result.returncode != 0:
        raise Exception("Behave tests failed!")

def run_locust():
    """Run Locust tests."""
    subprocess.run([
        "locust",
        "-f", "locustfile.py",
        "--host", "http://127.0.0.1:5000",
        "--users", "10",
        "--spawn-rate", "1",
        "--run-time", "1m",
        "--csv", "test_results",
        "--html", "test_report.html"
    ])

if __name__ == "__main__":
    run_behave_tests()  # Run functional tests first
    run_locust()        # If successful, run performance tests
