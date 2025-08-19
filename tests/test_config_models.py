from pathlib import Path
from src.core.config.loader import load_config


def test_valid_config(tmp_path: Path):
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
    cfg = load_config([p])
    assert cfg.simulation.t_end == 1.0
