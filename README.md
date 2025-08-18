# EUV Tin Droplet — Laser Pre-Pulse Simulation (MPh + COMSOL)

This project models the interaction of a high-energy laser pulse with a **2D planar** liquid tin droplet (sphere → pancake transition) for EUV lithography sources.  
It is implemented in **Python** using the [MPh](https://github.com/MPh-py/MPh) wrapper over the COMSOL Java API to automate geometry creation, physics/BC assignment, solving, and post-processing.

---

## ✨ Key Features

- **All-Python pipeline** via MPh (no manual GUI steps required).
- **Externalized parameters** (no hardcoding): global material/geometry/solver values in `global_parameters_pp_v2.txt`, laser/beam in `laser_parameters_pp_v2.txt`, and an analytic laser pulse `P(t)` in `Ppp_analytic_expression.txt`.
- Physics: Heat Transfer (HT), Transport of Diluted Species (TDS), Laminar Flow (SPF), **ALE** moving mesh, **surface tension**, **Marangoni**, **recoil pressure**, **evaporation** with latent-heat sink at the surface.
- **Fresnel absorption** at the droplet boundary with a Gaussian spatial profile and user-defined `P(t)`.
- **Reproducible outputs** (PNG + CSV) and a saved `.mph` model for GUI inspection.

---

## 📦 Repository Structure
.
├─ src/
│ └─ pp_model.py              # main MPh script (build → solve → post → save)
├─ data/
│ ├─ global_parameters_pp_v2.txt
│ ├─ laser_parameters_pp_v2.txt
│ └─ Ppp_analytic_expression.txt
├─ results/                   # outputs written here (PNG, CSV, MPH)
├─ pyproject.toml             # (optional) project metadata/deps if using uv sync
├─ requirements.txt           # (optional) fallback deps
└─ README.md


> Note: The script defaults to reading parameters from `data/` and writing all outputs to `results/`. You can override paths with CLI flags.

---

## 🔧 Requirements

- **COMSOL Multiphysics 6.2** (with Java API available) and a valid license.
- **Python 3.10+** (3.11/3.12/3.13 also fine).
- **MPh** (tested with 1.2.x) + **JPype1** (MPh installs it).
- Windows (primary target). Linux works similarly; see notes below.

---

## 🛠️ Setup

You can use **uv** (recommended) or plain **pip**.

### Option A — uv (recommended)

```bash
# from the repo root
uv venv EUV_SIM
# Windows PowerShell:
.\EUV_SIM\Scripts\Activate.ps1
# Bash (WSL/macOS/Linux):
source EUV_SIM/bin/activate

# Install dependencies
# If you have a pyproject.toml with deps:
uv sync
# OR, if you have requirements.txt:
uv pip install -r requirements.txt

# Ensure MPh is present (installs JPype1 too)
uv pip install mph

# Run from repo root (parameters are read from data/ by default)
python src/pp_model.py

# Parameter-only parse (no COMSOL, sanity check)
python src/pp_model.py --check-params-only

# Override time list and output directory
python src/pp_model.py --tlist "range(0, 5e-9, 400)" --outdir results
On success, you should see:

results/pp_temperature.png — temperature field snapshot

results/pp_T_vs_time.csv — temperature vs time (global metric)

results/pp_massloss_vs_time.csv — evaporative mass flux integral

results/pp_radius_vs_time.csv — apparent radius vs time

results/pp_model_created.mph — open this in the COMSOL GUI

If you prefer all outputs in results/, set those paths at the top of pp_model.py.

🧠 Physics & Couplings (high level)

Laser heating (boundary):
q_abs_2D = A_PP * (2/(pi*w0^2)) * P(t) * exp(-2*((x-x_beam)^2+(y-y_beam)^2)/w0^2) * max(0, nx)
Applied on the entire droplet surface; max(0, nx) masks the shadowed side.

Evaporation:
Tin vapor leaves the surface with flux J_evap (Hertz–Knudsen or diffusion-limited).
Latent heat sink in HT uses -L_v * J_evap on the same boundary.

Capillarity / Marangoni / Recoil:
sigma(T) = sigma0 + dSigma_dT (T − T_ref); tangential stress via dSigma_dT;
normal stress from p_recoil (e.g., proportional to p_sat(T) or absorbed intensity).

ALE:
Prescribed normal mesh velocity equals fluid normal velocity at the free surface;
free deformation smoothing elsewhere.
