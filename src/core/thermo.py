from __future__ import annotations

from typing import Callable


def p_sat_kumar(T: float, P_ref: float, Lv_mol: float, T_boil: float, R_const: float = 8.314) -> float:
    """Clausius–Clapeyron form used in Kumar 2D COMSOL model.

    Psat(T) = P_ref * exp( (Lv_mol/R)*(1/T_boil - 1/T) ), with T in K and Psat in Pa.
    - P_ref: reference pressure at boiling (e.g., 1 atm → 101325 Pa)
    - Lv_mol: molar latent heat [J/mol]
    - T_boil: boiling temperature [K]
    - R_const: universal gas constant [J/mol/K]
    """
    from math import exp

    return P_ref * exp((Lv_mol / R_const) * (1.0 / T_boil - 1.0 / T))


def get_p_sat_callable(option: str | None) -> Callable[[float], float]:
    """Provide a p_sat(T) function based on a named option.

    Currently supports 'kumar_sn' (tin, Kumar form with typical constants).
    Defaults to ambient pressure (no evaporation) if option is None or unknown.
    """
    if option and option.lower() == "kumar_sn":
        # Typical tin values: Lv_sn ~ 2.96e6 J/kg; M_sn ~ 118.71e-3 kg/mol → Lv_mol
        Lv_mol = 2.96e6 * 118.71e-3
        T_boil = 2875.0
        P_ref = 101325.0

        def f(T: float) -> float:
            return p_sat_kumar(T, P_ref=P_ref, Lv_mol=Lv_mol, T_boil=T_boil)

        return f

    def ambient(T: float) -> float:  # fallback
        return 0.0

    return ambient

