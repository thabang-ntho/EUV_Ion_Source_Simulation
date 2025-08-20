"""
Physics Manager Module

High-level physics interface management using MPh API.
Replaces low-level Java physics calls with pythonic physics.create() patterns.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PhysicsManager:
    """High-level physics manager using MPh API"""
    
    def __init__(self, model, selections: Dict[str, Any], materials: Dict[str, Any]):
        """
        Initialize physics manager
        
        Args:
            model: MPh model object
            selections: Dictionary of named selections
            materials: Dictionary of material definitions
        """
        self.model = model
        self.selections = selections
        self.materials = materials
        self.physics_interfaces = {}
        
    def setup_all_physics(self, variant: str = 'fresnel') -> Dict[str, Any]:
        """
        Setup all physics interfaces based on variant
        
        Args:
            variant: Model variant ('fresnel' or 'kumar')
            
        Returns:
            Dictionary of created physics interfaces
        """
        logger.info(f"Setting up all physics interfaces for {variant} variant")
        
        # Core physics - common to all variants
        self.physics_interfaces['ht'] = self._setup_heat_transfer(variant)
        
        # Variant-specific physics
        if variant == 'fresnel':
            self.physics_interfaces['tds'] = self._setup_species_transport()
            self.physics_interfaces['ale'] = self._setup_arbitrary_lagrangian_eulerian()
        elif variant == 'kumar':
            self.physics_interfaces['spf'] = self._setup_single_phase_flow()
            self.physics_interfaces['ale'] = self._setup_arbitrary_lagrangian_eulerian()
            
        logger.info(f"Created {len(self.physics_interfaces)} physics interfaces")
        return self.physics_interfaces
    
    def _setup_heat_transfer(self, variant: str) -> Any:
        """Setup heat transfer physics interface"""
        logger.info("Setting up Heat Transfer physics")
        
        # Create heat transfer interface
        ht = self.model.physics().create('HeatTransfer', tag='ht')
        
        # Assign to droplet domain
        ht_droplet = ht.create('HeatTransferInSolids', tag='ht_solid')
        ht_droplet.property('selection', self.selections['s_drop'])
        
        # Setup thermal properties
        ht_droplet.property('k_mat', 'userdef')  # Use material properties
        ht_droplet.property('rho_mat', 'userdef')
        ht_droplet.property('Cp_mat', 'userdef')
        
        # Boundary conditions - variant specific
        if variant == 'fresnel':
            self._setup_fresnel_heat_bcs(ht)
        elif variant == 'kumar':
            self._setup_kumar_heat_bcs(ht)
            
        return ht
    
    def _setup_fresnel_heat_bcs(self, ht: Any) -> None:
        """Setup Fresnel-specific heat transfer boundary conditions"""
        
        # Laser heat source on droplet surface
        heat_source = ht.create('HeatSource', tag='laser_heat')
        heat_source.property('selection', self.selections['s_laser'])
        heat_source.property('Q0', 'Q_laser')  # Will be defined as parameter
        
        # Convective cooling on exposed surfaces
        convection = ht.create('ConvectiveHeatFlux', tag='convective_cooling')
        convection.property('selection', self.selections['s_surf'])
        convection.property('h', 'h_conv')
        convection.property('Text', 'T_ambient')
        
        # Domain boundary conditions (typically insulated)
        for boundary in ['left', 'right', 'top', 'bottom']:
            insulation = ht.create('ThermalInsulation', tag=f'insul_{boundary}')
            insulation.property('selection', self.selections[f's_{boundary}'])
            
        logger.info("Applied Fresnel heat transfer boundary conditions")
    
    def _setup_kumar_heat_bcs(self, ht: Any) -> None:
        """Setup Kumar-specific heat transfer boundary conditions"""
        
        # Volumetric heat source in droplet
        vol_heat = ht.create('HeatSource', tag='vol_heat')
        vol_heat.property('selection', self.selections['s_drop'])
        vol_heat.property('Q0', 'Q_vol')  # Volumetric heat generation
        
        # Surface cooling
        cooling = ht.create('ConvectiveHeatFlux', tag='surface_cooling')
        cooling.property('selection', self.selections['s_surf'])
        cooling.property('h', 'h_cool')
        cooling.property('Text', 'T_ambient')
        
        logger.info("Applied Kumar heat transfer boundary conditions")
    
    def _setup_species_transport(self) -> Any:
        """Setup Transport of Diluted Species (TDS) physics"""
        logger.info("Setting up Species Transport physics")
        
        # Create TDS interface
        tds = self.model.physics().create('TransportOfDilutedSpecies', tag='tds')
        
        # Assign to gas domain only
        tds_gas = tds.create('TransportInPorousMedia', tag='tds_gas')
        tds_gas.property('selection', self.selections['s_gas'])
        
        # Species properties
        tds_gas.property('D_c', 'D_tin')  # Tin diffusivity in gas
        
        # Boundary conditions
        evaporation = tds.create('ConcentrationFlux', tag='evaporation')
        evaporation.property('selection', self.selections['s_surf'])
        evaporation.property('N0', 'J_evap')  # Evaporation flux from droplet
        
        # Domain boundaries (typically open)
        outlet = tds.create('OpenBoundary', tag='outlet_bc')
        outlet.property('selection', [
            self.selections['s_left'],
            self.selections['s_right'],
            self.selections['s_top'],
            self.selections['s_bottom']
        ])
        
        return tds
    
    def _setup_single_phase_flow(self) -> Any:
        """Setup Single Phase Flow (SPF) physics"""
        logger.info("Setting up Single Phase Flow physics")
        
        # Create SPF interface
        spf = self.model.physics().create('SinglePhaseFlow', tag='spf')
        
        # Assign to droplet domain
        spf_fluid = spf.create('FluidProperties', tag='spf_droplet')
        spf_fluid.property('selection', self.selections['s_drop'])
        
        # Fluid properties
        spf_fluid.property('rho_mat', 'userdef')
        spf_fluid.property('mu_mat', 'userdef')
        
        # Boundary conditions
        # No slip on droplet surface interacting with gas
        no_slip = spf.create('Wall', tag='wall_bc')
        no_slip.property('selection', self.selections['s_surf'])
        
        return spf
    
    def _setup_arbitrary_lagrangian_eulerian(self) -> Any:
        """Setup Arbitrary Lagrangian-Eulerian (ALE) physics for moving boundaries"""
        logger.info("Setting up ALE physics")
        
        # Create ALE interface
        ale = self.model.physics().create('ArbitraryLagrangianEulerian', tag='ale')
        
        # Assign to droplet domain for deformation
        ale_domain = ale.create('MovingDomain', tag='ale_droplet')
        ale_domain.property('selection', self.selections['s_drop'])
        
        # Free boundary on droplet surface
        free_boundary = ale.create('FreeBoundary', tag='free_surf')
        free_boundary.property('selection', self.selections['s_surf'])
        
        # Fixed boundaries on domain edges
        for boundary in ['left', 'right', 'top', 'bottom']:
            fixed = ale.create('FixedBoundary', tag=f'fixed_{boundary}')
            fixed.property('selection', self.selections[f's_{boundary}'])
            
        return ale
    
    def get_physics_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all physics interfaces"""
        info = {}
        for name, physics in self.physics_interfaces.items():
            info[name] = {
                'tag': physics.tag(),
                'type': physics.typename(),
                'active': physics.isActive()
            }
        return info
    
    def validate_physics_coupling(self) -> List[str]:
        """
        Validate physics interface coupling
        
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        # Check required physics exist
        required = ['ht']  # Heat transfer always required
        for req in required:
            if req not in self.physics_interfaces:
                issues.append(f"Required physics '{req}' not found")
        
        # Check physics compatibility
        if 'tds' in self.physics_interfaces and 'spf' in self.physics_interfaces:
            issues.append("TDS and SPF should not be used together")
            
        if issues:
            logger.warning(f"Physics validation found {len(issues)} issues")
        else:
            logger.info("Physics coupling validated successfully")
            
        return issues
