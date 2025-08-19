class SimError(Exception):
    ...


class ConfigError(SimError):
    ...


class PhysicsError(SimError):
    ...


class LicenseError(SimError):
    ...


class ComsolConnectError(SimError):
    ...


class DataError(SimError):
    ...
