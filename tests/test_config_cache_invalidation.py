from pathlib import Path
from src.core.config.loader import load_config


def test_config_cache_invalidation_by_content(tmp_path: Path, monkeypatch):
    cfg1 = tmp_path / "cfg.yaml"
    cfg1.write_text(
        """
simulation: {t_end: 1.0}
laser: {wavelength_um: 1.06}
absorption: {model: fresnel}
environment: {gas: none, pressure_torr: 1.33}
        """,
        encoding="utf-8",
    )
    c1 = load_config([cfg1])
    # Modify content
    cfg1.write_text(
        """
simulation: {t_end: 2.0}
laser: {wavelength_um: 1.06}
absorption: {model: fresnel}
environment: {gas: none, pressure_torr: 1.33}
        """,
        encoding="utf-8",
    )
    c2 = load_config([cfg1])
    assert c2.simulation.t_end == 2.0
    assert c1 is not c2

