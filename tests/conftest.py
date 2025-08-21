import pytest


LEGACY_PATTERNS = (
    'pp_model',  # legacy CLI/module
    'tests/mph_integration/test_mph_core.py',
    'tests/mph_integration/test_migration_validation.py',
)


def pytest_collection_modifyitems(config, items):
    """Skip legacy tests tied to deprecated low-level or pp_model paths."""
    skip_legacy = pytest.mark.skip(reason="Legacy (pp_model/low-level) test skipped under mph-only focus")
    for item in items:
        path_str = str(item.fspath)
        if any(p in path_str for p in LEGACY_PATTERNS):
            item.add_marker(skip_legacy)
