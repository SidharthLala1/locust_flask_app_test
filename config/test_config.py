class TestConfig:
    BASE_URL = "http://127.0.0.1:5000/"
    CONCURRENT_USERS = 10
    TEST_DURATION = 300  # 5 minutes
    SPAWN_RATE = 1
    MAX_RESPONSE_TIME = 2000  # milliseconds
    SUCCESS_RATE_THRESHOLD = 95  # percentage
    MIN_WAIT_TIME = 1000  # milliseconds
    MAX_WAIT_TIME = 3000  # milliseconds
    WAIT_TIME_MIN = 1
    WAIT_TIME_MAX = 2
    # Registration test configs
    REGISTRATION_ENDPOINT = "/client_registeration"
    # Login test configs
    LOGIN_ENDPOINT = "/client_login"
