import os
from pathlib import Path
from src.core.config.loader import load_config


def test_cache_invalidation_on_env_change(tmp_path: Path, monkeypatch):
    p = tmp_path / "cfg.yaml"
    p.write_text(
        """
simulation: {t_end: 1.0}
laser: {wavelength_um: 1.06}
absorption: {model: fresnel}
environment: {gas: none, pressure_torr: 1.33}
        """,
        encoding="utf-8",
    )
    cfg1 = load_config([p])
    monkeypatch.setenv("COMSOL_HOST", "localhost")
    cfg2 = load_config([p])
    assert cfg2.simulation.t_end == 1.0
    assert cfg1 is not cfg2

