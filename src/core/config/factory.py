from typing import Literal
from .models import RootConfig, Simulation, Laser, Absorption, Environment


def make_sim_config(kind: Literal["fresnel", "kumar"] = "fresnel") -> RootConfig:
    sim = Simulation(t_end=1.0)
    laser = Laser(wavelength_um=1.064, theta_deg=0.0)
    absorption = Absorption(model=kind)
    env = Environment()
    return RootConfig(simulation=sim, laser=laser, absorption=absorption, environment=env)

