from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .utils import parse_value_unit, unit_is_si


SCHEMA_VERSION = "0.1.0"


@dataclass
class SimulationConfig:
    time_end: float
    time_step_hint: Optional[float] = None
    solver_abs_tol: Optional[float] = None
    solver_rel_tol: Optional[float] = None


@dataclass
class GeometryConfig:
    R: float  # m
    Lx: float  # m
    Ly: float  # m
    x_beam: Optional[float] = None
    y_beam: Optional[float] = None


@dataclass
class MaterialsConfig:
    rho_Sn: float
    cp_Sn: float
    k_Sn: float
    mu_Sn: float
    M_Sn: float
    L_v: float
    sigma0: float
    dSigma_dT: float
    T_ref: float


@dataclass
class EnvironmentConfig:
    gas: str = "none"  # none|H2
    pressure_torr: Optional[float] = None
    p_amb: Optional[float] = None
    T_amb: Optional[float] = 300.0
    diffusivity_law: Optional[str] = None  # None|t175_over_p
    Dm0: Optional[float] = None  # base diffusivity [m^2/s]


@dataclass
class LaserConfig:
    A_PP: float
    w0: float
    E_PP_total: Optional[float] = None
    temporal_profile: Optional[str] = None  # gaussian|square|ramp_square
    tau_ramp: Optional[float] = None
    tau_square: Optional[float] = None
    laser_theta_deg: float = 0.0
    illum_mode: str = "cos_inc"  # cos_inc|nx_shadow


@dataclass
class AbsorptionConfig:
    model: str = "fresnel"  # fresnel|kumar
    use_nk: Optional[bool] = None
    nk_file: Optional[str] = None
    lambda_um: Optional[float] = None
    use_precomputed: Optional[bool] = None
    autogenerate_if_missing: Optional[bool] = None


@dataclass
class EvaporationConfig:
    HK_gamma: Optional[float] = None
    p_sat_option: Optional[str] = None  # e.g., kumar_sn
    p_sat_expr: Optional[str] = None  # string expression evaluated in COMSOL
    beta_r: Optional[float] = None
    clamp_nonneg: Optional[bool] = None


@dataclass
class RadiationConfig:
    emissivity: Optional[float] = None


@dataclass
class MeshConfig:
    refine_surface: Optional[bool] = None
    refine_beam_sigma: Optional[float] = None
    n_bl: Optional[int] = None
    bl_thick: Optional[float] = None
    evaporation_mesh: Optional[bool] = None


@dataclass
class OutputsConfig:
    out_dir: Optional[str] = None


@dataclass
class UnifiedConfig:
    schema_version: str
    simulation: SimulationConfig
    geometry: GeometryConfig
    materials: MaterialsConfig
    environment: EnvironmentConfig
    laser: LaserConfig
    absorption: AbsorptionConfig
    evaporation: EvaporationConfig
    radiation: RadiationConfig
    mesh: MeshConfig
    outputs: OutputsConfig
    raw: Dict[str, Any] = field(default_factory=dict)


def _require_range(name: str, val: float, lo: float, hi: float, closed: bool = True):
    if closed:
        ok = (lo <= val <= hi)
    else:
        ok = (lo <= val < hi)
    if not ok:
        raise ValueError(f"Parameter {name}={val} outside allowed range [{lo}, {hi}{']' if closed else ')'}")


def _warn(msg: str):
    warnings.warn(msg)


def validate_schema(cfg: Dict[str, Any]) -> None:
    # Types and required keys (minimal for now; extend as needed)
    sim = cfg["simulation"]
    if not isinstance(sim.get("time_end"), (int, float)):
        raise TypeError("simulation.time_end must be a number (seconds)")

    geom = cfg["geometry"]
    for k in ("R", "Lx", "Ly"):
        if not isinstance(geom.get(k), (int, float)):
            raise TypeError(f"geometry.{k} must be a number (meters)")
        _require_range(f"geometry.{k}", geom[k], 1e-9, 1.0)

    las = cfg["laser"]
    _require_range("laser.A_PP", las["A_PP"], 0.0, 1.0)
    if las.get("laser_theta_deg") is not None:
        _require_range("laser.laser_theta_deg", float(las["laser_theta_deg"]), 0.0, 360.0, closed=False)
    if las.get("illum_mode") not in ("cos_inc", "nx_shadow"):
        raise ValueError("laser.illum_mode must be one of {'cos_inc','nx_shadow'}")

    evap = cfg["evaporation"]
    if evap.get("beta_r") is not None:
        _require_range("evaporation.beta_r", float(evap["beta_r"]), 0.0, 1.0)
    if evap.get("clamp_nonneg") is not None and not isinstance(evap.get("clamp_nonneg"), bool):
        raise TypeError("evaporation.clamp_nonneg must be boolean if provided")

    # Units sanity for a few key fields (if provided as strings)
    hints: List[Tuple[str, str]] = [
        ("materials.M_Sn", "kg/mol"),
        ("materials.L_v", "J/kg"),
    ]
    for dotted, expected in hints:
        root, leaf = dotted.split(".")
        raw = cfg[root].get(leaf)
        if isinstance(raw, str):
            _, u = parse_value_unit(raw)
            if not unit_is_si(u, expected):
                _warn(f"Unit for {dotted} should be {expected} (got {u!r}); leaving as-is for COMSOL to interpret.")


def load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return data


def load_legacy(params_dir: Path) -> Dict[str, Any]:
    """Load the legacy text parameter files and pulse expression into a unified dict.

    This does not convert units; it surfaces keys under sections for validation.
    """
    from .legacy_loader import load_legacy_params

    return load_legacy_params(params_dir)


def create_config_from_dict(cfg: Dict[str, Any]) -> UnifiedConfig:
    validate_schema(cfg)
    return UnifiedConfig(
        schema_version=cfg.get("schema_version", SCHEMA_VERSION),
        simulation=SimulationConfig(**cfg["simulation"]),
        geometry=GeometryConfig(**cfg["geometry"]),
        materials=MaterialsConfig(**cfg["materials"]),
        environment=EnvironmentConfig(**cfg["environment"]),
        laser=LaserConfig(**cfg["laser"]),
        absorption=AbsorptionConfig(**cfg["absorption"]),
        evaporation=EvaporationConfig(**cfg["evaporation"]),
        radiation=RadiationConfig(**cfg["radiation"]),
        mesh=MeshConfig(**cfg["mesh"]),
        outputs=OutputsConfig(**cfg["outputs"]),
        raw=cfg,
    )


def load_config(params_dir: Optional[Path]) -> Tuple[UnifiedConfig, Dict[str, Any]]:
    """Load either a YAML unified config (preferred) or legacy files with migration.

    Returns (UnifiedConfig, raw_dict). Emits deprecation warnings for legacy.
    """
    params_dir = (params_dir or Path("data")).resolve()
    yaml_path = params_dir / "config.yaml"
    if yaml_path.is_file():
        raw = load_yaml(yaml_path)
        if "schema_version" not in raw:
            raw["schema_version"] = SCHEMA_VERSION
        ucfg = create_config_from_dict(raw)
        return ucfg, raw

    # Legacy path
    _warn(
        "Using legacy parameter files (global_parameters_pp_v2.txt, laser_parameters_pp_v2.txt). "
        "Please migrate to data/config.yaml."
    )
    raw = load_legacy(params_dir)
    ucfg = create_config_from_dict(raw)
    return ucfg, raw
