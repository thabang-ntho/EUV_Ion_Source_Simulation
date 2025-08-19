from pathlib import Path

from src.core.params import load_config


def test_load_yaml_config(tmp_path: Path):
    # Copy example config into tmp and load
    src = Path('data/config.yaml')
    dst_dir = tmp_path / 'data'
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / 'config.yaml'
    dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')

    cfg, raw = load_config(dst_dir)
    assert cfg.schema_version == '0.1.0'
    assert 0.0 <= cfg.laser.A_PP <= 1.0
    assert cfg.geometry.R > 0 and cfg.geometry.Lx > 0 and cfg.geometry.Ly > 0

