from behave.formatter.base import Formatter
import datetime
import time


class HTMLFormatter(Formatter):
    def __init__(self, stream_opener, config):
        super().__init__(stream_opener, config)
        self.stream = self.open()
        self.features = []
        self.current_feature = None
        self.current_scenario = None
        self.start_time = time.time()

    def uri(self, uri):
        pass

    def feature(self, feature):
        self.current_feature = {
            'name': feature.name,
            'scenarios': [],
            'status': 'passed',
            'tags': feature.tags
        }
        self.features.append(self.current_feature)

    def scenario(self, scenario):
        self.current_scenario = {
            'name': scenario.name,
            'steps': [],
            'status': 'passed',
            'tags': scenario.tags
        }
        self.current_feature['scenarios'].append(self.current_scenario)

    def step(self, step):
        step_data = {
            'name': step.name,
            'status': step.status,
            'duration': getattr(step, 'duration', 0),
            'error_message': getattr(step, 'error_message', '') if step.status == 'failed' else None
        }

        if hasattr(self, 'current_scenario'):
            self.current_scenario['steps'].append(step_data)

            if step.status == 'failed':
                self.current_scenario['status'] = 'failed'
                self.current_feature['status'] = 'failed'

    def eof(self):
        pass

    def close(self):
        duration = time.time() - self.start_time

        # Write HTML header
        self.stream.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Behave Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        .feature { margin-bottom: 30px; border: 1px solid #dee2e6; border-radius: 5px; padding: 15px; }
        .scenario { margin: 10px 0; padding: 10px; background: #fff; border-left: 4px solid #ccc; }
        .passed { border-left-color: #28a745; }
        .failed { border-left-color: #dc3545; }
        .step { margin: 5px 0 5px 20px; }
        .step.passed { color: #28a745; }
        .step.failed { color: #dc3545; }
        .error-message { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 4px; }
        .tag { background: #e9ecef; padding: 2px 6px; border-radius: 3px; margin-right: 5px; font-size: 0.9em; }
        .duration { color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Behave Test Results</h1>
""")

        # Write summary
        total_scenarios = sum(len(f['scenarios']) for f in self.features)
        passed_scenarios = sum(1 for f in self.features for s in f['scenarios'] if s['status'] == 'passed')
        failed_scenarios = total_scenarios - passed_scenarios

        self.stream.write(f"""
    <div class="summary">
        <h2>Test Summary</h2>
        <p>Total Scenarios: {total_scenarios}</p>
        <p>Passed: {passed_scenarios}</p>
        <p>Failed: {failed_scenarios}</p>
        <p>Duration: {duration:.2f} seconds</p>
    </div>
""")

        # Write feature details
        for feature in self.features:
            self.stream.write(f"""
    <div class="feature">
        <h2>{feature['name']}</h2>
        <div>{''.join(f'<span class="tag">{tag}</span>' for tag in feature['tags'])}</div>
""")

            for scenario in feature['scenarios']:
                self.stream.write(f"""
        <div class="scenario {scenario['status']}">
            <h3>{scenario['name']}</h3>
            <div>{''.join(f'<span class="tag">{tag}</span>' for tag in scenario['tags'])}</div>
""")

                for step in scenario['steps']:
                    self.stream.write(f"""
            <div class="step {step['status']}">
                {step['name']} <span class="duration">({step['duration']:.3f}s)</span>
            </div>
""")
                    if step['error_message']:
                        self.stream.write(f"""
            <div class="error-message">
                <pre>{step['error_message']}</pre>
            </div>
""")

                self.stream.write("        </div>")
            self.stream.write("    </div>")

        self.stream.write("""
</body>
</html>
""")
        self.stream.close()
