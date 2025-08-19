from src.core.logging_utils import write_provenance

def test_provenance(tmp_path):
    meta = write_provenance(tmp_path, {"k": "v"}, "fresnel")
    assert (tmp_path / "provenance.json").exists()
    assert meta["variant"] == "fresnel"
