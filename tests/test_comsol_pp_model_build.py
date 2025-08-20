import os
import shutil
from pathlib import Path
import subprocess
import sys
import pytest


pytestmark = [
    pytest.mark.comsol,
    pytest.mark.skipif(os.environ.get("RUN_COMSOL") != "1", reason="COMSOL local-only; set RUN_COMSOL=1 to enable"),
]


def test_pp_model_build_no_solve_cli(tmp_path: Path):
    repo = Path(__file__).resolve().parents[1]
    data_src = repo / "data"
    # Prepare temp params dir by copying known-good legacy files
    for fn in ("global_parameters_pp_v2.txt", "laser_parameters_pp_v2.txt", "Ppp_analytic_expression.txt"):
        shutil.copyfile(data_src / fn, tmp_path / fn)

    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, "-m", "src.pp_model", "--no-solve", "--absorption-model", "fresnel", "--params-dir", str(tmp_path), "--out-dir", str(out_dir), "--emit-milestones"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"CLI failed: {res.stderr}\n{res.stdout}"
    mph = out_dir / "pp_model_created.mph"
    assert mph.is_file(), f"Expected MPH at {mph}"

