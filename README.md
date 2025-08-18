# EUV Tin Droplet — Laser Pre-Pulse Simulation (MPh + COMSOL)

This project models the interaction of a high-energy laser pulse with a **2D planar** liquid tin droplet (sphere → pancake transition) for EUV lithography sources.
It is implemented in **Python** using the [MPh](https://github.com/MPh-py/MPh) wrapper over the COMSOL Java API to automate geometry creation, physics/BC assignment, solving, and post-processing.

---

## ✨ Key Features

- **All-Python pipeline** via MPh (no manual GUI steps required).
- **Externalized parameters** (no hardcoding): global material/geometry/solver values in `global_parameters_pp_v2.txt`, laser/beam in `laser_parameters_pp_v2.txt`, and an analytic laser pulse `P(t)` in `Ppp_analytic_expression.txt`.
- **Advanced Physics:** Heat Transfer (HT), Transport of Diluted Species (TDS), Laminar Flow (SPF), **ALE** moving mesh, **surface tension**, **Marangoni effect**, **recoil pressure**, and **Hertz-Knudsen evaporation** with a latent-heat sink.
- **Robust Laser Modeling:** Fresnel absorption at the droplet boundary with a Gaussian spatial profile and user-defined `P(t)`. Includes an automatic "shadowing" effect.
- **Reproducible outputs** (PNG + CSV) and a saved `.mph` model with custom views for easy GUI inspection.

---

## 📦 Repository Structure
```
.
├─ src/
│ └─ pp_model.py              # Main MPh script (build → solve → post → save)
├─ data/
│ ├─ global_parameters_pp_v2.txt
│ ├─ laser_parameters_pp_v2.txt
│ └─ Ppp_analytic_expression.txt
├─ results/                   # Outputs written here (PNG, CSV, MPH)
├─ EVAPORATION_PHYSICS_REFERENCE/ # Reference COMSOL model for evaporation
├─ pyproject.toml             # Project metadata and dependencies for uv
├─ requirements.txt           # Dependencies for pip
└─ README.md
```

> Note: The script defaults to reading parameters from `data/` and writing all outputs to `results/`. You can override these paths with CLI flags.

---

## 🔧 Requirements

- **COMSOL Multiphysics 6.2** (with Java API available) and a valid license.
- **Python 3.10+**.
- **MPh** library (installs automatically with the steps below).

---

## 🛠️ Setup

You can use **uv** (recommended) or plain **pip**.

### Option A — uv (Recommended)

```bash
# Create a virtual environment
uv venv

# Activate the environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Bash (Linux/macOS):
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Option B — pip

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the Simulation

```bash
# Run from the repository root
python src/pp_model.py

# Run with custom output and parameter directories
python src/pp_model.py --params-dir ./data --out-dir ./results

# Run without solving to just generate the .mph model file
python src/pp_model.py --no-solve
```

On a successful run, you will find the following in your output directory:
- `pp_temperature.png`: Snapshot of the temperature field.
- `pp_T_vs_time.csv`: Time history of the average temperature.
- `pp_massloss_vs_time.csv`: Time history of the total mass loss rate.
- `pp_radius_vs_time.csv`: Time history of the droplet radius.
- `pp_model_created.mph`: The COMSOL model file, which you can open in the GUI. It includes a custom "Droplet View" for easier inspection.

---

## 🧠 Physics & Couplings

### Laser Heating (Boundary)
The laser is modeled as a boundary heat source applied to the droplet surface. The heat flux `q_abs_2D` is defined as:
`q_abs_2D = A_PP * I_xy * max(0, nx)`
where `I_xy` is the Gaussian spatial profile of the laser beam. The `max(0, nx)` term cleverly ensures that the heat is only applied to the laser-facing side of the droplet (where the x-component of the surface normal `nx` is positive), automatically creating a shadow region.

### Evaporation Physics
The model uses the **Hertz-Knudsen** equation to describe the evaporative mass flux `J_evap` from the droplet surface, which is appropriate for evaporation into a vacuum or low-pressure environment. This flux is coupled to:
- **Heat Transfer:** A latent heat sink (`-L_v * J_evap`) is applied to the droplet surface, modeling evaporative cooling.
- **Species Transport:** The `Transport of Diluted Species` interface uses the evaporative flux as a source term.
- **Moving Mesh:** The `ALE` interface uses the fluid velocity at the surface (which is affected by evaporation) to deform the mesh.

### Advanced Fluid Dynamics
The `Laminar Flow` interface includes several important effects for modeling laser-droplet interaction:
- **Surface Tension:** Standard surface tension forces.
- **Marangoni Effect:** Surface tension gradients caused by temperature differences on the droplet surface.
- **Recoil Pressure:** Pressure exerted on the surface by the evaporating material.