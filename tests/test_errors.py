from src.core.errors import LicenseError, ComsolConnectError


def test_error_messages():
    try:
        raise LicenseError("License error: verify COMSOL_HOME and license server")
    except LicenseError as e:
        assert "license" in str(e).lower()
    try:
        raise ComsolConnectError("Could not connect to COMSOL: check server and Java bindings")
    except ComsolConnectError as e:
        assert "comsol" in str(e).lower()
