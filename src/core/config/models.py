from pydantic import BaseModel, Field, AliasChoices, ConfigDict
from typing import Literal, Optional


class Simulation(BaseModel):
    # Accept both 't_end' and legacy 'time_end' from YAML
    t_end: float = Field(..., gt=0, description="End time [s]", validation_alias=AliasChoices("t_end", "time_end"))
    dt_init: Optional[float] = Field(None, gt=0, description="Initial time step [s]")
    solver: Literal["direct", "iterative"] = "direct"


class Laser(BaseModel):
    # Wavelength not always required in current YAML; make optional
    wavelength_um: Optional[float] = Field(None, gt=0)
    theta_deg: float = Field(0, ge=0, lt=360, description="Incidence angle [deg]")


class Absorption(BaseModel):
    model: Literal["fresnel", "kumar"] = "fresnel"
    use_precomputed: bool = True
    autogenerate_if_missing: bool = True
    nk_file: Optional[str] = None
    lambda_um: Optional[float] = Field(None, gt=0, description="Sampling wavelength for A")


class Environment(BaseModel):
    gas: Literal["none", "H2"] = "none"
    pressure_torr: float = Field(1.33, gt=0)


# Extend as needed for geometry/materials/evaporation/radiation/mesh/outputs
class RootConfig(BaseModel):
    """Minimal structured config for additive validation in tests.

    This model is intentionally small and frozen to encourage immutable use.
    """
    model_config = ConfigDict(frozen=True)

    schema_version: Optional[str] = Field(default=None, description="Schema version string, if provided")
    simulation: Simulation
    laser: Laser
    absorption: Absorption
    environment: Environment
