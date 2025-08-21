# Kumar 2D — MPh Translation and Runner

Self‑contained MPh (Python) translation of the COMSOL Java model `Kumar_2D_demo_v5.java` based on the Kumar paper (Manoj_RAJA_KUMAR.pdf). Implements geometry, selections, materials, physics, mesh, studies, and saves a `.mph` model.

Contents
- `parameters.txt`: model parameters (with units) used by both runners.
- `kumar_2d_mph.py`: direct MPh container‑API translation; builds (and optionally solves) a `.mph`.
- `run_kumar_mph.py`: architecture‑aligned runner using `src/mph_core` (`ModelBuilder` with `variant='kumar'`).
- `data/`, `results/`: self‑contained inputs/outputs for this folder.

Prerequisites
- COMSOL Multiphysics 6.2+ (local session recommended for build‑only).
- Python 3.10+ and the `mph` package (installed via project venv).

Environment setup
- Activate repo venv (Python):
  - `. .venv/bin/activate`
- COMSOL (local 6.2 on this system): `mph` finds COMSOL automatically. For remote servers, set:
  - `export COMSOL_HOST=<host>`
  - `export COMSOL_PORT=<port>`
- Optional gate for COMSOL tests/runs:
  - `export RUN_COMSOL=1`

Quick runs (no COMSOL)
- Dry‑run (plans only):
  - `python KUMAR-2D/kumar_2d_mph.py --dry-run`
  - `python KUMAR-2D/run_kumar_mph.py --dry-run`

Build `.mph` (check‑only)
- Direct translation:
  - `RUN_COMSOL=1 python KUMAR-2D/kumar_2d_mph.py --check-only --out KUMAR-2D/results/kumar2d_model.mph`
- Architecture‑aligned (`mph_core`):
  - `RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --check-only --out KUMAR-2D/results/kumar2d_model.mph`

Solve (optional, requires COMSOL)
- Local/hosted server:
  - `RUN_COMSOL=1 python KUMAR-2D/run_kumar_mph.py --solve --host $COMSOL_HOST --port $COMSOL_PORT --out KUMAR-2D/results/kumar2d_model.mph`

Outputs
- `results/kumar2d_model.mph` (build‑only)
- `results/kumar2d_model_solved.mph` (after solve)
- Optional result plots via `src/mph_core/postprocess.py`

Implemented physics and boundary conditions (paper‑faithful)
- Domains and physics:
  - Heat Transfer in Fluids (droplet): `ht` on `s_drop`.
  - Heat Transfer in Fluids (gas): `ht2` on `s_gas`.
  - Laminar Flow (droplet): `spf` on `s_drop` (Marangoni tangential stress on interface).
  - Laminar Flow (gas): `spf2` on `s_gas` (recoil normal stress on interface).
  - Transport of Diluted Species (gas): `tds` on `s_gas` (tin vapor in H₂).
- Laser heating (surface Gaussian at metal/gas interface):
  - `Qb_input = (2*a_abs*P_laser)/(pi*Rl_spot^2) * exp(-2*((x-x0)^2+(y-y0)^2)/Rl_spot^2) * pulse(t)/1[s]`
  - Applied on droplet surface selection `s_surf` in `ht`.
- Evaporation latent heat:
  - Liquid side (cooling): `- Lv_sn*J_evap` (combined into the `Qb_input` expression above).
  - Gas side (heating): `+ Lv_sn*J_evap` in `ht2` at `s_surf`.
- Recoil pressure (gas interface):
  - Normal stress on `s_surf`: `f0 = -(1 + beta_r/2) * Psat(T)` in `spf2`.
- Marangoni stress (droplet interface):
  - Tangential stress ∝ surface tension gradient (via `d_sigma_dT`), set on `spf` at `s_surf`.
- Species flux (evaporation):
  - Interface flux in `tds` on `s_surf`: `N0 = J_evap/M_sn` (flip sign if inward‑positive convention is preferred).
- Saturation pressure and evaporation rate:
  - `Psat(T) = P_ref * exp( (Lv_sn*M_sn/R_gas) * (1/Tboil_sn - 1/T) )`
  - `J_evap = (1 - beta_r) * Psat(T) * sqrt( M_sn/(2*pi*R_gas*T) )`
- Functions and variables:
  - `pulse(t) = flc2hs(t - t_start, eps_t) - flc2hs(t - (t_start + t_pulse), eps_t)`
  - `x0=y0=0` by default (laser centered on droplet).

Mesh and studies
- Mesh: size refinement on `s_drop`, boundary layer on `s_surf` (`n`, `thickness`) + `FreeTri`.
- Study: time‑dependent step including all Kumar physics; solver tolerances configurable via parameters.

Notes and troubleshooting
- If you see unknown geometry/mesh tag issues, ensure the mesh is created via `meshes.create(geometry, ...)` and feature selections use named selections (`s_drop`, `s_surf`).
- For environment/usage details, see `docs/mph/user_guide.md` (COMSOL host/port, RUN_COMSOL, etc.).
