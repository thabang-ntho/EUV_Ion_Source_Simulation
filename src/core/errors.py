class SimError(Exception):
    """Base simulation error with optional suggested fix string."""

    def __init__(self, message: str, suggested_fix: str | None = None):
        super().__init__(message)
        self.suggested_fix = suggested_fix


class ConfigError(SimError):
    pass


class PhysicsError(SimError):
    pass


class LicenseError(SimError):
    pass


class ComsolConnectError(SimError):
    pass


class DataError(SimError):
    pass

# Standardized exit codes for CLI
EXIT_OK = 0
EXIT_CONFIG = 2
EXIT_LICENSE = 3
EXIT_RUNTIME = 4
