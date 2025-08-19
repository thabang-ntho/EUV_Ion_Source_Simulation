# Parameter Reference (Unified Schema)

- simulation:
  - time_end: total simulated time [s]
  - time_step_hint: optional solver step hint [s]
  - solver_abs_tol, solver_rel_tol: optional tolerances

- geometry:
  - R, Lx, Ly: droplet radius and box size [m]
  - x_beam, y_beam: beam center [m]

- materials:
  - rho_Sn [kg/m^3], cp_Sn [J/kg/K], k_Sn [W/m/K], mu_Sn [Pa*s]
  - M_Sn [kg/mol], L_v [J/kg]
  - sigma0 [N/m], dSigma_dT [N/m/K], T_ref [K]

- environment:
  - gas: none|H2
  - pressure_torr: background pressure [Torr]
  - p_amb: ambient pressure for Fresnel HK form [Pa]
  - T_amb: ambient temperature [K]

- laser:
  - A_PP: absorptivity (0–1)
  - w0: 1/e^2 beam radius [m]
  - E_PP_total: pulse energy [J]
  - temporal_profile: gaussian|square|ramp_square (optional P(t) override)
  - tau_ramp, tau_square [s]; laser_theta_deg [deg]; illum_mode: cos_inc|nx_shadow

- absorption:
  - model: fresnel|kumar
  - use_nk: compute A_PP from n,k at lambda_um (Sizyuk); default false
  - nk_file: path to n,k Excel file (e.g., data/nk_tin.xlsx)
  - lambda_um: wavelength in micrometers (e.g., 1.064)

- evaporation:
  - HK_gamma: Hertz–Knudsen coefficient (Fresnel path)
  - beta_r: recombination coefficient (Kumar path)
  - p_sat_option: e.g., kumar_sn (uses Clausius–Clapeyron with Sn defaults)
  - p_sat_expr: explicit expression string in COMSOL syntax (Pa, K)

- radiation:
  - emissivity: hemispherical emissivity (0–1)

- mesh:
  - refine_surface: boolean
  - refine_beam_sigma: factor around w0
  - n_bl: boundary layer elements; bl_thick: thickness [m]
  - evaporation_mesh: enable evaporation-driven normal mesh motion (Kumar)

- outputs:
  - out_dir: output directory path

Notes
- Units are SI. Provide K for temperature and Pa for pressures. Psat(T) must be in Pa.
- Use either YAML or legacy TXT; YAML is preferred and validated with `--check-only`.
