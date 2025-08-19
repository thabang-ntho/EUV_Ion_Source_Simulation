from types import SimpleNamespace

from src.core import build as build_mod


def test_compute_A_PP_from_nk_monkeypatch(monkeypatch, tmp_path):
    # Prepare a dummy nk file path (not actually read; loader is monkeypatched)
    nk_file = tmp_path / "nk_dummy.xlsx"
    nk_file.write_text("dummy", encoding="utf-8")

    # Build a dummy cfg with absorption settings
    absorption = SimpleNamespace(use_nk=True, nk_file=str(nk_file), lambda_um=1.0)
    cfg = SimpleNamespace(absorption=absorption)

    # Monkeypatch loader to return simple arrays and absorptivity fn to a known value
    def fake_load_nk_excel(path):
        lam = [0.5, 1.0, 2.0]
        n = [2.0, 2.0, 2.0]
        k = [3.0, 3.0, 3.0]
        return lam, n, k

    def fake_absorptivity_from_nk(lam_um, lam_arr, n_arr, k_arr, n_medium=1.0):
        # Reflectance R = ((n-1)^2 + k^2)/((n+1)^2 + k^2); A = 1-R
        # For n=2, k=3 → R = ((1)^2+9)/((3)^2+9) = 10/18 = 5/9 → A = 4/9 ≈ 0.444444...
        return 4.0/9.0

    monkeypatch.setattr(build_mod, "_load_nk_excel", fake_load_nk_excel, raising=True)
    monkeypatch.setattr(build_mod, "_absorptivity_from_nk", fake_absorptivity_from_nk, raising=True)

    A = build_mod.compute_A_PP_from_nk(cfg)
    assert A is not None
    assert abs(A - 4.0/9.0) < 1e-9
