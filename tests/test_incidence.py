import math


def cos_incidence(nx: float, ny: float, theta_deg: float) -> float:
    th = math.radians(theta_deg)
    kx, ky = math.cos(th), math.sin(th)
    return max(0.0, - (nx * kx + ny * ky))


def nx_shadow(nx: float) -> float:
    return max(0.0, nx)


def test_incidence_shadowing_front_back():
    # Surface normal pointing -x (west-facing)
    nx, ny = -1.0, 0.0
    # Laser along +x → heats west face only
    assert cos_incidence(nx, ny, 0.0) > 0.0
    assert cos_incidence(+1.0, 0.0, 0.0) == 0.0
    # 90 deg rotates to +y; west face gets zero (tolerate fp epsilon)
    assert abs(cos_incidence(nx, ny, 90.0)) < 1e-12


def test_nx_shadow_legacy_behavior():
    assert nx_shadow(+0.1) == 0.1
    assert nx_shadow(-0.1) == 0.0
