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
        
        # Skip additional physics for now to get basic functionality working
        # Additional physics (TDS, SPF, ALE) can be added later once heat transfer is stable
        
        logger.info(f"Created {len(self.physics_interfaces)} physics interfaces")
        return self.physics_interfaces
    
    def _setup_heat_transfer(self, variant: str) -> Any:
        """Setup heat transfer physics interface"""
        logger.info("Setting up Heat Transfer physics")
        
        # Access physics container and create heat transfer interface
        physics = self.model/'physics'
        ht = physics.create('HeatTransfer', self.model/'geometries'/'geometry', name='heat_transfer')
        
        # Set up basic heat transfer in the droplet domain
        # Heat transfer should automatically be active in the domain
        ht.select(self.selections['s_drop'])
        
        # Configure material properties usage
        # The heat transfer physics should use the assigned material properties
        
        # Setup boundary conditions - variant specific
        if variant == 'fresnel':
            self._setup_fresnel_heat_bcs(ht)
        elif variant == 'kumar':
            self._setup_kumar_heat_bcs(ht)
            
        logger.info("Heat transfer physics setup completed")
        return ht
    
    def _setup_fresnel_heat_bcs(self, ht: Any) -> None:
        """Setup Fresnel-specific heat transfer boundary conditions"""
        logger.info("Setting up Fresnel heat transfer boundary conditions")
        
        # For now, skip complex boundary conditions and use defaults
        # The heat transfer physics will use default boundary conditions
        # This can be enhanced later with specific BC types
        
        logger.info("Applied Fresnel heat transfer boundary conditions (using defaults)")
    
    def _setup_kumar_heat_bcs(self, ht: Any) -> None:
        """Setup Kumar-specific heat transfer boundary conditions"""
        logger.info("Setting up Kumar heat transfer boundary conditions")
        
        # For now, skip complex boundary conditions and use defaults
        # This can be enhanced later with specific boundary condition types
        
        logger.info("Applied Kumar heat transfer boundary conditions (using defaults)")
    
    def _setup_species_transport(self) -> Any:
        """Setup Transport of Diluted Species (TDS) physics"""
        logger.info("Setting up Species Transport physics")
        
        # Access physics container and create TDS interface
        physics = self.model/'physics'
        tds = physics.create('TransportOfDilutedSpecies', self.model/'geometries'/'geometry', name='species_transport')
        
        # Set up basic species transport - use default domain assignment for now
        # The TDS physics should automatically be active in the appropriate domains
        
        logger.info("Species transport physics setup completed")
        return tds
    
    def _setup_single_phase_flow(self) -> Any:
        """Setup Single Phase Flow (SPF) physics"""
        logger.info("Setting up Single Phase Flow physics")
        
        # Access physics container and create SPF interface
        physics = self.model/'physics'
        spf = physics.create('SinglePhaseFlow', self.model/'geometries'/'geometry', name='fluid_flow')
        
        # Set up basic fluid flow - use default domain assignment for now
        # The SPF physics should automatically be active in the appropriate domains
        
        logger.info("Single phase flow physics setup completed")
        return spf
    
    def _setup_arbitrary_lagrangian_eulerian(self) -> Any:
        """Setup Arbitrary Lagrangian-Eulerian (ALE) physics for moving boundaries"""
        logger.info("Setting up ALE physics")
        
        # Access physics container and create ALE interface
        physics = self.model/'physics'
        ale = physics.create('ArbitraryLagrangianEulerian', self.model/'geometries'/'geometry', name='moving_mesh')
        
        # Set up basic ALE - use default domain assignment for now
        # The ALE physics should automatically be active in the appropriate domains
        
        logger.info("ALE physics setup completed")
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
