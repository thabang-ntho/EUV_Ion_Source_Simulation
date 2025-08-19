from src.core.thermo import p_sat_kumar


def test_psat_monotonic_tin_like():
    P_ref = 101325.0
    Lv_mol = 2.96e6 * 118.71e-3
    T_boil = 2875.0
    vals = [p_sat_kumar(T, P_ref, Lv_mol, T_boil) for T in range(500, 2501, 100)]
    assert all(x2 > x1 for x1, x2 in zip(vals, vals[1:])), "p_sat(T) must increase with T"
    # For T < T_boil, Psat < P_ref; for T increasing, Psat increases but remains below P_ref here
    assert vals[0] < P_ref and vals[-1] < P_ref
