"""
MPh Integration Test Configuration

Pytest configuration for MPh integration tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def test_output_dir():
    """Create temporary directory for test outputs"""
    temp_dir = Path(tempfile.mkdtemp(prefix='euv_mph_test_'))
    yield temp_dir
    
    # Cleanup after tests
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def clean_test_environment(test_output_dir):
    """Provide clean test environment for each test"""
    test_subdir = test_output_dir / f"test_{id(pytest.current_request)}"
    test_subdir.mkdir(exist_ok=True)
    
    original_cwd = Path.cwd()
    
    yield test_subdir
    
    # Cleanup
    try:
        if test_subdir.exists():
            shutil.rmtree(test_subdir)
    except:
        pass  # Best effort cleanup


@pytest.fixture
def mock_comsol_unavailable():
    """Fixture for tests that assume COMSOL is not available"""
    # This fixture can be used to skip tests that require COMSOL
    # when running in CI/CD environments
    return True


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "mph_integration: marks tests as MPh integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_comsol: marks tests that require COMSOL installation"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "validation: marks tests as validation/regression tests"
    )


def pytest_runtest_setup(item):
    """Setup for individual test runs"""
    # Skip COMSOL-requiring tests in CI
    if item.get_closest_marker("requires_comsol"):
        try:
            import mph
            mph.start()  # Test connection
        except:
            pytest.skip("COMSOL not available")


# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Mark all tests in mph_integration directory
        if "mph_integration" in str(item.fspath):
            item.add_marker(pytest.mark.mph_integration)
            
        # Mark validation tests
        if "validation" in item.name or "regression" in item.name:
            item.add_marker(pytest.mark.validation)
            
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ['complete', 'integration', 'full']):
            item.add_marker(pytest.mark.slow)
