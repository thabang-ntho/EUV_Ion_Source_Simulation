"""
MPh Fresnel Variant

Fresnel-specific model implementation using MPh API.
Focus on evaporation and species transport physics.
"""

from typing import Dict, Any
from pathlib import Path
import logging

from ..mph_core.model_builder import ModelBuilder

logger = logging.getLogger(__name__)


class FresnelModelBuilder(ModelBuilder):
    """Fresnel variant model builder using MPh API"""
    
    def __init__(self, params: Dict[str, Any]):
        """Initialize Fresnel model builder"""
        super().__init__(params, variant='fresnel')
        
        # Fresnel-specific parameters
        self._setup_fresnel_defaults()
    
    def _setup_fresnel_defaults(self) -> None:
        """Setup Fresnel-specific default parameters"""
        
        fresnel_defaults = {
            # Laser parameters
            'Laser_Power': 1e6,  # W/m² - laser intensity
            'Laser_Spot_Radius': 10e-6,  # m - laser spot size
            'Laser_Pulse_Duration': 10e-9,  # s - pulse duration
            'Laser_Wavelength': 1064e-9,  # m - Nd:YAG laser
            
            # Evaporation parameters
            'Evaporation_Coefficient': 0.8,  # evaporation coefficient
            'Saturation_Pressure_Coeff': 1e10,  # Pa - pressure coefficient
            'Activation_Energy': 3e5,  # J/mol - evaporation activation energy
            
            # Species transport
            'Tin_Diffusivity_Gas': 1e-5,  # m²/s - Sn diffusion in gas
            'Gas_Type': 'argon',  # Background gas
            'Gas_Pressure': 1e5,  # Pa - ambient pressure
            
            # Simulation time
            'Time_End': 100e-9,  # s - simulation end time
            'Time_Step_Initial': 1e-12,  # s - initial time step
            'Time_Step_Max': 1e-10,  # s - maximum time step
            
            # Output settings
            'Output_Time_Points': 100,  # number of output times
            'Temperature_Min_Plot': 300,  # K - plot range
            'Temperature_Max_Plot': 3000,  # K - above tin boiling point
        }
        
        # Apply defaults (don't override existing values)
        for key, value in fresnel_defaults.items():
            if key not in self.params:
                self.params[key] = value
                
        logger.info("Applied Fresnel-specific defaults")
    
    def _setup_physics(self) -> None:
        """Setup Fresnel-specific physics (override parent)"""
        logger.info("Setting up Fresnel physics interfaces")
        
        # Call parent method first
        super()._setup_physics()
        
        # Add Fresnel-specific physics configurations
        self._configure_fresnel_heat_transfer()
        self._configure_species_transport()
        self._configure_evaporation_kinetics()
        
    def _configure_fresnel_heat_transfer(self) -> None:
        """Configure heat transfer with laser heating"""
        logger.info("Configuring Fresnel heat transfer")
        
        ht = self.physics_manager.physics_interfaces['ht']
        
        # Laser heat source parameters
        laser_power = self.params['Laser_Power']
        laser_radius = self.params['Laser_Spot_Radius']
        absorptivity = self.params.get('Tin_Absorptivity', 0.8)
        
        # Gaussian laser profile
        laser_profile = f"{absorptivity}*{laser_power}*exp(-2*((x^2+y^2)/{laser_radius}^2))"
        
        # Update laser heat source
        laser_heat = ht.feature('laser_heat')
        laser_heat.property('Q0', laser_profile)
        laser_heat.property('name', 'Gaussian Laser Heat Source')
        
        # Temperature-dependent convection
        h_conv_base = self.params.get('Convection_Coefficient', 100)  # W/(m²·K)
        h_conv_expr = f"{h_conv_base}*(1 + 0.01*(T-300[K]))"  # Temperature dependent
        
        convection = ht.feature('convective_cooling')
        convection.property('h', h_conv_expr)
        convection.property('Text', f"{self.params.get('Ambient_Temperature', 300)}[K]")
        
        logger.info("Configured Fresnel heat transfer with Gaussian laser profile")
    
    def _configure_species_transport(self) -> None:
        """Configure species transport for tin evaporation"""
        logger.info("Configuring species transport")
        
        if 'tds' not in self.physics_manager.physics_interfaces:
            logger.warning("TDS physics not found for species transport")
            return
            
        tds = self.physics_manager.physics_interfaces['tds']
        
        # Tin diffusivity in gas
        D_tin = self.params['Tin_Diffusivity_Gas']
        tds_gas = tds.feature('tds_gas')
        tds_gas.property('D_c', f"{D_tin}[m^2/s]")
        
        # Background concentration (very low)
        tds_gas.property('c_init', '1e-6[mol/m^3]')
        
        logger.info("Configured species transport for tin vapor")
    
    def _configure_evaporation_kinetics(self) -> None:
        """Configure evaporation boundary condition"""
        logger.info("Configuring evaporation kinetics")
        
        if 'tds' not in self.physics_manager.physics_interfaces:
            return
            
        tds = self.physics_manager.physics_interfaces['tds']
        evaporation = tds.feature('evaporation')
        
        # Hertz-Knudsen evaporation equation
        evap_coeff = self.params['Evaporation_Coefficient']
        P_sat_coeff = self.params['Saturation_Pressure_Coeff']
        E_act = self.params['Activation_Energy']
        R_gas = 8.314  # J/(mol·K)
        M_tin = 0.1187  # kg/mol - tin molar mass
        
        # Saturation pressure (Clausius-Clapeyron)
        P_sat_expr = f"{P_sat_coeff}*exp(-{E_act}/({R_gas}*T))"
        
        # Evaporation flux (Hertz-Knudsen)
        J_evap_expr = f"{evap_coeff}*{P_sat_expr}/sqrt(2*pi*{R_gas}*T/{M_tin})"
        
        evaporation.property('N0', J_evap_expr)
        evaporation.property('name', 'Hertz-Knudsen Evaporation')
        
        logger.info("Configured Hertz-Knudsen evaporation kinetics")
    
    def get_fresnel_info(self) -> Dict[str, Any]:
        """Get Fresnel-specific model information"""
        info = self.get_model_info()
        
        info['fresnel_specific'] = {
            'laser_power': self.params['Laser_Power'],
            'laser_spot_radius': self.params['Laser_Spot_Radius'],
            'evaporation_coefficient': self.params['Evaporation_Coefficient'],
            'gas_type': self.params['Gas_Type'],
            'simulation_time': self.params['Time_End']
        }
        
        return info


def build_fresnel_model(params: Dict[str, Any], output_path: Path = None) -> Path:
    """
    Convenience function to build complete Fresnel model
    
    Args:
        params: Parameter dictionary
        output_path: Output .mph file path
        
    Returns:
        Path to saved model file
    """
    logger.info("Building complete Fresnel model")
    
    with FresnelModelBuilder(params) as builder:
        model_file = builder.build_complete_model(output_path)
        
        # Optionally solve and extract results
        if params.get('Solve_Immediately', False):
            results = builder.solve_and_extract_results()
            logger.info(f"Extracted results: {list(results.keys())}")
            
        return model_file
