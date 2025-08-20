"""
MPh Kumar Variant

Kumar-specific model implementation using MPh API.
Focus on fluid flow and thermal dynamics with deformation.
"""

from typing import Dict, Any
from pathlib import Path
import logging

from ..mph_core.model_builder import ModelBuilder

logger = logging.getLogger(__name__)


class KumarModelBuilder(ModelBuilder):
    """Kumar variant model builder using MPh API"""
    
    def __init__(self, params: Dict[str, Any]):
        """Initialize Kumar model builder"""
        super().__init__(params, variant='kumar')
        
        # Kumar-specific parameters
        self._setup_kumar_defaults()
    
    def _setup_kumar_defaults(self) -> None:
        """Setup Kumar-specific default parameters"""
        
        kumar_defaults = {
            # Volumetric heating parameters
            'Volumetric_Heat_Generation': 1e12,  # W/m³ - volumetric heat source
            'Heat_Decay_Time': 10e-9,  # s - heat generation decay
            'Heat_Distribution_Width': 20e-6,  # m - heating zone width
            
            # Fluid flow parameters
            'Reynolds_Number': 1000,  # characteristic Reynolds number
            'Weber_Number': 100,  # characteristic Weber number
            'Capillary_Number': 0.1,  # Ca = μv/(σ)
            
            # Surface tension effects
            'Surface_Tension_Temperature_Coeff': -1e-4,  # N/(m·K) - dσ/dT
            'Marangoni_Effect': True,  # enable Marangoni convection
            
            # ALE parameters
            'Mesh_Smoothing': 'laplace',  # mesh smoothing method
            'Boundary_Relaxation': 0.1,  # boundary relaxation factor
            
            # Simulation time
            'Time_End': 50e-9,  # s - shorter simulation time
            'Time_Step_Initial': 1e-12,  # s - initial time step
            'Time_Step_Max': 5e-11,  # s - maximum time step
            
            # Output settings
            'Output_Time_Points': 50,  # fewer output points
            'Temperature_Min_Plot': 300,  # K
            'Temperature_Max_Plot': 2000,  # K
            'Velocity_Max_Plot': 100,  # m/s - maximum velocity for plots
        }
        
        # Apply defaults (don't override existing values)
        for key, value in kumar_defaults.items():
            if key not in self.params:
                self.params[key] = value
                
        logger.info("Applied Kumar-specific defaults")
    
    def _setup_physics(self) -> None:
        """Setup Kumar-specific physics (override parent)"""
        logger.info("Setting up Kumar physics interfaces")
        
        # Call parent method first
        super()._setup_physics()
        
        # Add Kumar-specific physics configurations
        self._configure_kumar_heat_transfer()
        self._configure_fluid_flow()
        self._configure_ale_deformation()
        self._setup_physics_coupling()
        
    def _configure_kumar_heat_transfer(self) -> None:
        """Configure heat transfer with volumetric heating"""
        logger.info("Configuring Kumar heat transfer")
        
        ht = self.physics_manager.physics_interfaces['ht']
        
        # Volumetric heat source
        Q_vol = self.params['Volumetric_Heat_Generation']
        tau_decay = self.params['Heat_Decay_Time']
        width = self.params['Heat_Distribution_Width']
        
        # Time-dependent volumetric heating with Gaussian distribution
        Q_expr = f"{Q_vol}*exp(-t/{tau_decay})*exp(-((x^2+y^2)/{width}^2))"
        
        vol_heat = ht.feature('vol_heat')
        vol_heat.property('Q0', Q_expr)
        vol_heat.property('name', 'Time-Dependent Volumetric Heating')
        
        # Enhanced convective cooling
        h_cool_base = self.params.get('Convection_Coefficient', 500)  # Higher for Kumar
        h_cool_expr = f"{h_cool_base}*(1 + 0.02*(T-300[K]))"
        
        cooling = ht.feature('surface_cooling')
        cooling.property('h', h_cool_expr)
        cooling.property('Text', f"{self.params.get('Ambient_Temperature', 300)}[K]")
        
        logger.info("Configured Kumar heat transfer with volumetric heating")
    
    def _configure_fluid_flow(self) -> None:
        """Configure single phase flow with surface tension effects"""
        logger.info("Configuring fluid flow")
        
        if 'spf' not in self.physics_manager.physics_interfaces:
            logger.warning("SPF physics not found for fluid flow")
            return
            
        spf = self.physics_manager.physics_interfaces['spf']
        spf_fluid = spf.feature('spf_droplet')
        
        # Temperature-dependent viscosity (Arrhenius-type)
        mu_ref = self.params.get('Tin_Viscosity_Liquid', 1.85e-3)  # Pa·s
        T_ref = self.params.get('Tin_Melting_Temperature', 505.08)  # K
        E_visc = 2e4  # J/mol - viscosity activation energy
        R_gas = 8.314  # J/(mol·K)
        
        mu_expr = f"{mu_ref}*exp({E_visc}/{R_gas}*(1/T - 1/{T_ref}[K]))"
        spf_fluid.property('mu', mu_expr)
        
        # Buoyancy force due to thermal expansion
        beta_thermal = self.params.get('Thermal_Expansion_Coefficient', 1e-4)  # 1/K
        g = 9.81  # m/s² - gravity
        
        # Add body force for natural convection
        body_force = spf.create('BodyForce', tag='buoyancy')
        body_force.property('selection', self.selection_manager.selections['s_drop'])
        buoyancy_expr = f"-rho*{g}*{beta_thermal}*(T-{T_ref}[K])"
        body_force.property('F', ['0', buoyancy_expr])
        
        # Surface tension boundary condition
        if self.params.get('Marangoni_Effect', True):
            self._add_marangoni_effect(spf)
            
        logger.info("Configured fluid flow with temperature-dependent properties")
    
    def _add_marangoni_effect(self, spf) -> None:
        """Add Marangoni stress boundary condition"""
        logger.info("Adding Marangoni effect")
        
        # Surface tension gradient
        gamma_0 = self.params.get('Tin_Surface_Tension', 0.544)  # N/m
        dgamma_dT = self.params['Surface_Tension_Temperature_Coeff']  # N/(m·K)
        
        # Marangoni stress
        marangoni = spf.create('SurfaceForce', tag='marangoni')
        marangoni.property('selection', self.selection_manager.selections['s_surf'])
        
        # Tangential stress due to temperature gradient
        # τ = ∇_s(γ) where ∇_s is surface gradient operator
        stress_expr = f"({gamma_0} + {dgamma_dT}*T)"
        marangoni.property('surface_tension', stress_expr)
        
        logger.info("Added Marangoni stress boundary condition")
    
    def _configure_ale_deformation(self) -> None:
        """Configure ALE for mesh deformation"""
        logger.info("Configuring ALE deformation")
        
        if 'ale' not in self.physics_manager.physics_interfaces:
            logger.warning("ALE physics not found")
            return
            
        ale = self.physics_manager.physics_interfaces['ale']
        
        # Free boundary with surface tension
        free_surf = ale.feature('free_surf')
        
        # Surface tension force
        gamma = self.params.get('Tin_Surface_Tension', 0.544)
        free_surf.property('surface_tension', f"{gamma}[N/m]")
        
        # Mesh smoothing
        ale_domain = ale.feature('ale_droplet')
        smoothing_method = self.params['Mesh_Smoothing']
        ale_domain.property('smoothing', smoothing_method)
        
        # Boundary relaxation for stability
        relaxation = self.params['Boundary_Relaxation']
        free_surf.property('relaxation', relaxation)
        
        logger.info("Configured ALE with surface tension and smoothing")
    
    def _setup_physics_coupling(self) -> None:
        """Setup coupling between physics interfaces"""
        logger.info("Setting up physics coupling")
        
        # Temperature-dependent material properties are automatically coupled
        
        # Velocity-dependent heat transfer (advection)
        if 'ht' in self.physics_manager.physics_interfaces and 'spf' in self.physics_manager.physics_interfaces:
            ht = self.physics_manager.physics_interfaces['ht']
            ht_solid = ht.feature('ht_solid')
            
            # Add convective heat transfer
            ht_solid.property('u_velocity', ['u', 'v'])  # Velocity field from SPF
            
        # ALE mesh velocity coupling
        if 'ale' in self.physics_manager.physics_interfaces and 'spf' in self.physics_manager.physics_interfaces:
            spf = self.physics_manager.physics_interfaces['spf']
            spf_fluid = spf.feature('spf_droplet')
            
            # Include mesh velocity in fluid equations
            spf_fluid.property('mesh_velocity', True)
            
        logger.info("Configured physics coupling")
    
    def get_kumar_info(self) -> Dict[str, Any]:
        """Get Kumar-specific model information"""
        info = self.get_model_info()
        
        info['kumar_specific'] = {
            'volumetric_heat_generation': self.params['Volumetric_Heat_Generation'],
            'reynolds_number': self.params['Reynolds_Number'],
            'weber_number': self.params['Weber_Number'],
            'marangoni_effect': self.params['Marangoni_Effect'],
            'simulation_time': self.params['Time_End']
        }
        
        return info


def build_kumar_model(params: Dict[str, Any], output_path: Path = None) -> Path:
    """
    Convenience function to build complete Kumar model
    
    Args:
        params: Parameter dictionary
        output_path: Output .mph file path
        
    Returns:
        Path to saved model file
    """
    logger.info("Building complete Kumar model")
    
    with KumarModelBuilder(params) as builder:
        model_file = builder.build_complete_model(output_path)
        
        # Optionally solve and extract results
        if params.get('Solve_Immediately', False):
            results = builder.solve_and_extract_results()
            logger.info(f"Extracted results: {list(results.keys())}")
            
        return model_file
