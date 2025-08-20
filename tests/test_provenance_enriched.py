from pathlib import Path
from src.core.logging_utils import write_provenance


def test_provenance_enriched(tmp_path: Path):
    meta = write_provenance(tmp_path, {"k": "v"}, "fresnel")
    assert (tmp_path / "provenance.json").exists()
    assert "software" in meta and "python" in meta["software"]
    assert "git" in meta and "commit" in meta["git"]

