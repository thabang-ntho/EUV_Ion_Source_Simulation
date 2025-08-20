import warnings
from pathlib import Path
from src.core.config.loader import load_config


def test_schema_version_mismatch_warns(tmp_path: Path):
    p = tmp_path / "cfg.yaml"
    p.write_text(
        """
schema_version: 9.9
simulation: {t_end: 1.0}
laser: {wavelength_um: 1.06}
absorption: {model: fresnel}
environment: {gas: none, pressure_torr: 1.33}
        """,
        encoding="utf-8",
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = load_config([p])
        assert cfg.simulation.t_end == 1.0
        assert any("schema_version mismatch" in str(item.message) for item in w)

