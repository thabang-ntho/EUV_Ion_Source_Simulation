import os
import sys
import subprocess
from pathlib import Path
import pytest


pytestmark = [
    pytest.mark.comsol,
    pytest.mark.skipif(os.environ.get("RUN_COMSOL") != "1", reason="COMSOL local-only; set RUN_COMSOL=1 to enable"),
]


def test_euv_mph_build_only(tmp_path: Path):
    out = tmp_path / "smoke_model.mph"
    cmd = [sys.executable, "-m", "src.cli.mph_runner", "--check-only", "--variant", "fresnel", "--output", str(out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI failed: {res.stderr}\n{res.stdout}"
    assert out.exists(), f"Expected MPH at {out}"

