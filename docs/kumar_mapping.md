# Kumar (COMSOL) → Our Code Mapping

- Domain assignments:
  - COMSOL Domain 1: Gas (H2 background)
  - COMSOL Domain 2: Tin droplet
  - Our code: `s_gas` selection → gas; `s_drop` selection → droplet

- Laser heat source (boundary):
  - COMSOL: `q_laser = (2*a_abs*P_laser)/(pi*Rl_spot^2) * exp(-2*r^2/Rl_spot^2) * pulse(t)/1[s]` on interface boundaries (IDs 5–8)
  - Our code (Fresnel variant): `q_abs_2D = A_PP*I_xy*inc_factor` with direction-aware incidence; for Kumar variant set `inc_factor = 1` (no Fresnel/shadowing) and surface Gaussian

- Latent heat coupling:
  - COMSOL (droplet HT): `Qb = q_laser - L_v * J_evap`
  - COMSOL (gas HT): `Qb = + L_v * J_evap`
  - Our code: `ht` boundary heat source uses `q_abs_2D - L_v*J_evap`; add `ht_gas` with `+L_v*J_evap` when `--absorption-model kumar`

- Evaporation mass flux (Hertz–Knudsen):
  - COMSOL: `J_evap = (1 - beta_r) * Psat * sqrt(M_sn/(2*pi*R_const*T))`
  - Our code (current): `J_evap = HK_gamma*(p_sat(T)-p_amb)/sqrt(2*pi*R_gas*T/M_Sn)`
  - Plan: Under Kumar variant, adopt COMSOL form with `beta_r` and `Psat(T)`; keep legacy under Fresnel

- Saturation vapor pressure:
  - COMSOL: `Psat(T) = P_ref * exp( (Lv_mol/R)*(1/Tboil - 1/T) )` with `P_ref=1 atm`, `Tboil=2875 K`
  - Our code: function `p_sat(T)` set from `p_sat_expr` or ambient; `core.thermo.p_sat_kumar` implements Kumar default.

- Recoil pressure / normal stress:
  - COMSOL (gas side): normal stress `f0 = -(1 + beta_r/2) * Psat`
  - Our code: `p_recoil = recoil_coeff*p_sat(T)` applied as pressure on droplet side; for Kumar variant, switch to gas-side normal stress form

- Marangoni + surface tension:
  - COMSOL: shear `-dσ/dT * (∂T/∂τ)` on interface; temp-dependent `σ(T)`
  - Our code: `sigmaT = sigma0 + dSigma_dT*(T-T_ref)` + Marangoni feature; consistent

- Species transport (gas):
  - COMSOL: `tds` in gas domain, boundary flux `J0 = J_evap / M_sn`, T-dependent `D ~ T^1.75 / p`
  - Our code: `tds` present with flux `-J_evap`; for Kumar variant, adapt to molar flux and T,p dependence if flag enabled

- Radiation:
  - COMSOL: material RadiationHeatTransfer group `Qrad(T)` for gas; emissivity on surface
  - Our code: not explicit; add optional radiative loss feature flag with emissivity

- Mesh motion (ALE):
  - COMSOL: mesh normal velocity `v_n = J_evap / rho_sn`; stiffness factor `S` based on displacement
  - Our code: ALE with mesh follows fluid `u·n`; add optional `v_n` term for evaporation-driven interface when Kumar variant enabled

- Environment:
  - COMSOL: H2 gas at ~10 mTorr; nonisothermal flow couplings `nitf1`, `nitf2`
  - Our code: default vacuum; add `environment.gas = none|H2`, `environment.pressure_torr`

