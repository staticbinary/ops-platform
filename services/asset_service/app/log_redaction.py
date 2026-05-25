SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
    "apikey",
    "client_secret",
}


def redact_value(key: str, value):
    normalized_key = key.lower()

    if normalized_key in SENSITIVE_KEYS:
        return "[REDACTED]"

    return value


def redact_log_data(data):
    if isinstance(data, dict):
        return {
            key: redact_log_data(redact_value(key, value))
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [redact_log_data(item) for item in data]

    return data