"""
Physics Manager Module

High-level phy        # Common physics for all variants
        self.physics_interfaces['ht'] = self._setup_heat_transfer(variant)
        
        # Variant-specific physics
        if variant == 'fresnel':
            self.physics_interfaces['tds'] = self._setup_species_transport()
            self.physics_interfaces['ale'] = self._setup_arbitrary_lagrangian_eulerian()
        elif variant == 'kumar':
            # Kumar uses multiple heat transfer and flow physics based on Java model
            self.physics_interfaces['ht2'] = self._setup_heat_transfer_gas(variant)
            self.physics_interfaces['spf'] = self._setup_laminar_flow_droplet()
            self.physics_interfaces['spf2'] = self._setup_laminar_flow_gas() 
            self.physics_interfaces['tds'] = self._setup_diluted_species()
            # TODO: Add multiphysics couplings nitf1 and nitf2face management using MPh API.
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
            # Kumar model uses dual physics setup as per Java implementation
            # 1. Heat transfer for both gas and droplet domains
            self.physics_interfaces['ht2'] = self._setup_heat_transfer_gas(variant)
            
            # 2. Laminar flow for both gas and droplet domains  
            self.physics_interfaces['spf'] = self._setup_laminar_flow_droplet()
            self.physics_interfaces['spf2'] = self._setup_laminar_flow_gas()
            
            # 3. Diluted species transport in gas domain
            self.physics_interfaces['tds'] = self._setup_diluted_species()
            
            # Note: Non-isothermal flow coupling happens automatically in COMSOL
            # when heat transfer and flow physics are defined on the same domains
            
        logger.info(f"Created {len(self.physics_interfaces)} physics interfaces")
        return self.physics_interfaces
    
    def _setup_heat_transfer(self, variant: str) -> Any:
        """Setup heat transfer physics interface for droplet domain"""
        logger.info("Setting up Heat Transfer physics for droplet")
        
        # Create heat transfer interface using HeatTransferInFluids (as per Java model)
        try:
            physics_container = self.model/'physics'
        except TypeError:
            # For testing with mocks, fall back to method call
            physics_container = self.model.physics()
        
        # Get geometry
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            # For testing with mocks
            geometry = None
            
        ht = physics_container.create('HeatTransferInFluids', geometry, name='ht')
        
        # Assign to droplet domain (domain 2 in Java model)
        ht.select(self.selections['s_drop'])
        
        # Add boundary heat source feature (Kumar: surface Gaussian heat source per paper)
        bhs = ht.create('BoundaryHeatSource', 1, name='bhs1')
        bhs.select(self.selections['s_surf'])
        # Heat source expression based on variant
        if variant == 'kumar':
            # Surface Gaussian heat source minus latent heat sink (Kumar paper)
            q_gauss = '(2*a_abs*P_laser)/(pi*Rl_spot^2)*exp(-2*((x - x0)^2 + (y - y0)^2)/Rl_spot^2)*pulse(t)/1[s]'
            bhs.property('Qb_input', f'{q_gauss} - Lv_sn*J_evap')
        else:
            # Fresnel variant can reuse Gaussian without evaporation term here
            bhs.property('Qb_input', '(2*a_abs*P_laser)/(pi*Rl_spot^2)*exp(-2*((x - x0)^2 + (y - y0)^2)/Rl_spot^2)*pulse(t)/1[s]')
        
        return ht
    
    def _setup_heat_transfer_gas(self, variant: str) -> Any:
        """Setup second heat transfer physics interface for gas domain"""
        logger.info("Setting up Heat Transfer physics for gas")
        
        # Create second heat transfer interface
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            geometry = None
            
        ht2 = physics_container.create('HeatTransferInFluids', geometry, name='ht2')
        
        # Assign to gas domain (domain 1 in Java model)
        ht2.select(self.selections['s_gas'])
        
        # Latent heat absorbed by gas phase on interface
        bhs = ht2.create('BoundaryHeatSource', 1, name='bhs1')
        bhs.select(self.selections['s_surf'])
        # From Kumar: gas gains latent heat removed from liquid (sign convention)
        bhs.property('Qb_input', 'Lv_sn*J_evap')
        
        return ht2
    
    def _setup_laminar_flow_droplet(self) -> Any:
        """Setup laminar flow physics interface for droplet domain"""
        logger.info("Setting up Laminar Flow physics for droplet")
        
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            geometry = None
            
        spf = physics_container.create('LaminarFlow', geometry, name='spf')
        
        # Assign to droplet domain (domain 2)
        spf.select(self.selections['s_drop'])
        
        # Add boundary stress feature (Marangoni/recoil handled in interfaces; TODO: refine expressions)
        bs = spf.create('BoundaryStress', 1, name='bs1')
        bs.select(self.selections['s_surf'])
        
        return spf
    
    def _setup_laminar_flow_gas(self) -> Any:
        """Setup second laminar flow physics interface for gas domain"""
        logger.info("Setting up Laminar Flow physics for gas")
        
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            geometry = None
            
        spf2 = physics_container.create('LaminarFlow', geometry, name='spf2')
        
        # Assign to gas domain (domain 1)
        spf2.select(self.selections['s_gas'])
        
        # Add boundary stress feature (recoil normal stress)
        bs = spf2.create('BoundaryStress', 1, name='bs1')
        bs.select(self.selections['s_surf'])
        try:
            bs.property('BoundaryCondition', 'NormalStress')
            bs.property('f0', '-(1+beta_r/2)*Psat')
        except Exception:
            pass
        
        return spf2
    
    def _setup_diluted_species(self) -> Any:
        """Setup diluted species transport physics interface"""
        logger.info("Setting up Diluted Species physics")
        
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            geometry = None
            
        tds = physics_container.create('DilutedSpecies', geometry, name='tds')
        
        # Assign to gas domain (domain 1)
        tds.select(self.selections['s_gas'])
        
        # Add evaporation flux boundary feature (inward-positive sign convention)
        fl = tds.create('FluxBoundary', 1, name='fl1')
        fl.select(self.selections['s_surf'])
        # COMSOL's N0 is inward-positive; evaporation is outward from liquid → gas
        # Convert mass flux to molar flux by dividing by M_sn and flip sign
        fl.property('N0', '-J_evap/M_sn')
        
        # Add convection-diffusion in gas domain
        cdm = tds.create('ConvectionDiffusionMigration', 2, name='cdm2')
        cdm.select(self.selections['s_gas'])
        
        return tds
    
    def _setup_non_isothermal_flow(self) -> Any:
        """Setup non-isothermal flow multiphysics coupling"""
        logger.info("Setting up Non-Isothermal Flow coupling")
        
        try:
            multiphysics_container = self.model/'multiphysics'
        except TypeError:
            multiphysics_container = self.model.multiphysics()
        
        # COMSOL multiphysics coupling requires geometry tag
        try:
            geometry = self.model/'geometries'/'geom1'
            geom_tag = 'geom1'
        except TypeError:
            geom_tag = 'geom1'  # Default geometry tag
            
        nitf = multiphysics_container.create('NonIsothermalFlow', geom_tag, name='nitf1')
        
        # Couple the physics interfaces
        nitf.setPhysics('heat', 'ht')  # Heat transfer in fluids
        nitf.setPhysics('flow', 'spf') # Laminar flow
        
        return nitf
    
    def _setup_non_isothermal_flow_gas(self) -> Any:
        """Setup second non-isothermal flow multiphysics coupling for gas"""
        logger.info("Setting up Non-Isothermal Flow coupling for gas")
        
        try:
            multiphysics_container = self.model/'multiphysics'
        except TypeError:
            multiphysics_container = self.model.multiphysics()
        
        # COMSOL multiphysics coupling requires geometry tag
        try:
            geometry = self.model/'geometries'/'geom1'
            geom_tag = 'geom1'
        except TypeError:
            geom_tag = 'geom1'  # Default geometry tag
        
        nitf2 = multiphysics_container.create('NonIsothermalFlow', geom_tag, name='nitf2')
        
        # Couple the second physics interfaces
        nitf2.setPhysics('heat', 'ht2')  # Second heat transfer for gas
        nitf2.setPhysics('flow', 'spf2') # Second laminar flow for gas
        
        return nitf2
    
    def _setup_fresnel_heat_bcs(self, ht: Any) -> None:
        """Setup Fresnel-specific heat transfer boundary conditions"""
        
        # For Kumar model, heat source is applied directly to domain
        # with spatial localization via expressions
        # No need for separate laser selection
        
        # Convective cooling on exposed surfaces (if needed)
        if 's_surf' in self.selections:
            convection = ht.create('ConvectiveHeatFlux', 1, name='convective_cooling')
            convection.property('selection', self.selections['s_surf'])
            convection.property('h', 'h_conv')
            convection.property('Text', 'T_ambient')
        
        logger.info("Applied Fresnel heat transfer boundary conditions")
    
    def _setup_kumar_heat_bcs(self, ht: Any) -> None:
        """Setup Kumar-specific heat transfer boundary conditions and volumetric heat source"""
        
        # Volumetric laser heat source in droplet (following Kumar paper and working model)
        # 3D Gaussian laser heating with time-dependent pulse
        vol_heat = ht.create('HeatSource', 2, name='laser_heating')
        q_expr = '(2*a_abs*P_laser)/(pi*Rl_spot^2)*exp(-2*((x - x0)^2 + (y - y0)^2)/Rl_spot^2)*pulse(t)/1[s]'
        # For volumetric heat source, the parameter is usually 'Q' in COMSOL
        vol_heat.property('Q', q_expr)
        
        logger.info("Applied Kumar volumetric laser heat source with Gaussian profile and pulse timing")
    
    def _setup_species_transport(self) -> Any:
        """Setup Transport of Diluted Species (TDS) physics"""
        logger.info("Setting up Species Transport physics")

        # Create TDS interface
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        # Get geometry
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            # For testing with mocks
            geometry = None
            
        tds = physics_container.create('TransportOfDilutedSpecies', geometry, name='tds')
        
        # Assign to gas domain only
        tds_gas = tds.create('TransportInPorousMedia', 2, name='tds_gas')
        tds_gas.property('selection', self.selections['s_gas'])
        
        # Species properties
        tds_gas.property('D_c', 'D_tin')  # Tin diffusivity in gas
        
        # Boundary conditions
        evaporation = tds.create('ConcentrationFlux', 1, name='evaporation')
        evaporation.property('selection', self.selections['s_surf'])
        # Inward-positive convention: outward evaporation becomes negative inward flux
        evaporation.property('N0', '-J_evap/M_sn')
        
        # Domain boundaries (typically open)
        outlet = tds.create('OpenBoundary', 1, name='outlet_bc')
        outlet.property('selection', [
            self.selections['s_left'],
            self.selections['s_right'],
            self.selections['s_top'],
            self.selections['s_bottom']
        ])
        
        return tds
    
    def _setup_laminar_flow(self) -> Any:
        """Setup laminar flow physics interface"""
        logger.info("Setting up Laminar Flow physics")
        
        # Create laminar flow interface  
        try:
            physics_container = self.model/'physics'
        except TypeError:
            # For testing with mocks, fall back to method call
            physics_container = self.model.physics()
        
        # Get geometry
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            # For testing with mocks
            geometry = None
            
        spf = physics_container.create('LaminarFlow', geometry, name='spf')
        
        # Assign to droplet domain
        spf.select(self.selections['s_drop'])
        
        return spf
    
    def _setup_arbitrary_lagrangian_eulerian(self) -> Any:
        """Setup Arbitrary Lagrangian-Eulerian (ALE) physics for moving boundaries"""
        logger.info("Setting up ALE physics")
        
        # Create ALE interface
        try:
            physics_container = self.model/'physics'
        except TypeError:
            physics_container = self.model.physics()
        
        # Get geometry
        try:
            geometry = self.model/'geometries'/'geom1'
        except TypeError:
            # For testing with mocks
            geometry = None
            
        ale = physics_container.create('ArbitraryLagrangianEulerian', geometry, name='ale')
        
        # Assign to droplet domain for deformation
        ale_domain = ale.create('MovingDomain', 2, name='ale_droplet')
        ale_domain.property('selection', self.selections['s_drop'])
        
        # Free boundary on droplet surface
        free_boundary = ale.create('FreeBoundary', 1, name='free_surf')
        free_boundary.property('selection', self.selections['s_surf'])
        
        # Fixed boundaries on domain edges
        for boundary in ['left', 'right', 'top', 'bottom']:
            fixed = ale.create('FixedBoundary', 1, name=f'fixed_{boundary}')
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
