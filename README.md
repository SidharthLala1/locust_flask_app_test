# Flask API Load Testing Project

This project contains a comprehensive suite of load and stress testing scripts for a Flask API using Locust. The testing suite focuses on two main endpoints: user registration and login functionality.
In reports folder there are two reports already generated using locust for both the end points.

## Table of Contents
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Generating Reports](#generating-reports)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Project Structure
```
locust_tests/
├── config/
│   └── test_config.py      # Configuration settings
├── scenarios/
│   ├── registration_test.py # Registration endpoint tests
│   └── login_test.py       # Login endpoint tests
├── data/
│   └── test_users.json     # Test data
└── requirements.txt        # Project dependencies
```

## Prerequisites
## Note the flask app should be running to generate successful report.
- Python 3.8 or higher
- pip (Python package installer)
- Flask API running locally or on a test server
- Sufficient system resources for load testing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd locust_flask_app_test
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

### Basic Configuration
All test configurations are stored in `config/test_config.py`. Key configurations include:

```python
HOST = "http://localhost:5000"  # API host
MIN_WAIT_TIME = 1000           # Minimum wait time between requests (ms)
MAX_WAIT_TIME = 3000           # Maximum wait time between requests (ms)
USERS_COUNT = 1000             # Number of users for testing
```

### Endpoint Configuration
- Registration endpoint: `/client_registeration`
- Login endpoint: `/client_login`

## Running Tests

### Registration Load Testing

1. Basic load test:
```bash
locust -f locust_scenarios/registration_test.py --users 50 --spawn-rate 10 --run-time 5m
```

2. Heavy load test:
```bash
locust -f locust_scenarios/registration_test.py --users 100 --spawn-rate 20 --run-time 10m
```

3. Spike test:
```bash
locust -f locust_scenarios/registration_test.py --users 200 --spawn-rate 50 --run-time 15m
```

### Login Stress Testing

1. Baseline test:
```bash
locust -f locust_scenarios/login_test.py --users 100 --spawn-rate 10 --run-time 5m
```

2. Stress test:
```bash
locust -f locust_scenarios/login_test.py --users 500 --spawn-rate 50 --run-time 10m
```

3. Breaking point test:
```bash
locust -f locust_scenarios/login_test.py --users 1000 --spawn-rate 100 --run-time 15m
```

## Test Scenarios

### Registration Load Testing Scenarios

1. **Normal Load**
   - Users: 50
   - Spawn Rate: 10 users/second
   - Duration: 5 minutes
   - Purpose: Baseline performance measurement

2. **Heavy Load**
   - Users: 100
   - Spawn Rate: 20 users/second
   - Duration: 10 minutes
   - Purpose: Testing system under sustained heavy load

3. **Spike Test**
   - Users: 200
   - Spawn Rate: 50 users/second
   - Duration: 15 minutes
   - Purpose: Testing system response to sudden traffic spikes

### Login Stress Testing Scenarios

1. **Baseline**
   - Users: 100
   - Spawn Rate: 10 users/second
   - Duration: 5 minutes
   - Purpose: Establishing baseline performance

2. **Stress Test**
   - Users: 500
   - Spawn Rate: 50 users/second
   - Duration: 10 minutes
   - Purpose: Testing system limits

3. **Breaking Point**
   - Users: 1000
   - Spawn Rate: 100 users/second
   - Duration: 15 minutes
   - Purpose: Identifying system breaking point

## Generating Reports

Locust provides several ways to generate reports:

1. Web Interface (Default):
   - Start Locust without --headless flag
   - Access http://localhost:8089
   - Download reports from the web UI

2. CSV Reports:
```bash
locust -f locust_scenarios/registration_test.py --csv=reports/registration_test
```

3. HTML Report:
```bash
locust -f locust_scenarios/registration_test.py --html=reports/registration_test.html
```
