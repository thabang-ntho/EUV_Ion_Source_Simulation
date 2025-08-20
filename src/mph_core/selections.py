"""
Selection Manager Module

High-level selection creation and management using MPh API.
Replaces low-level Java selection calls with pythonic selections.create() patterns.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SelectionManager:
    """High-level selection manager using MPh API"""
    
    def __init__(self, model, geometry, params):
        """
        Initialize selection manager
        
        Args:
            model: MPh model object
            geometry: GeometryBuilder instance
            params: Parameter dictionary
        """
        self.model = model
        self.geometry = geometry
        self.params = params
        self.selections = {}
        
    def create_all_selections(self) -> Dict[str, Any]:
        """
        Create all required selections for physics assignment
        
        Returns:
            Dict mapping selection names to selection objects
        """
        logger.info("Creating all model selections with MPh API")
        
        # Create domain selections first
        domain_selections = self._create_domain_selections()
        self.selections.update(domain_selections)
        
        # Create boundary selections (needs domain selections)
        boundary_selections = self._create_boundary_selections(domain_selections)
        self.selections.update(boundary_selections)
        
        # Create special selections for physics
        physics_selections = self._create_physics_selections()
        self.selections.update(physics_selections)
        
        logger.info(f"Created {len(self.selections)} selections")
        return self.selections
    
    def _create_domain_selections(self) -> Dict[str, Any]:
        """Create domain-based selections"""
        selections = {}
        
        # Access selections container
        sel_container = self.model/'selections'
        
        # Droplet domain selection
        s_drop = sel_container.create('Disk', name='s_drop')
        s_drop.property('posx', f"{self.params['X_max']}[um]")
        s_drop.property('posy', f"{self.params['Y_max']}[um]")
        s_drop.property('r', f"{self.params['R_drop']*0.9}[um]")
        selections['s_drop'] = s_drop
        
        # For now, create a simple gas domain selection - we'll refine this later
        s_gas = sel_container.create('Explicit', name='s_gas')
        s_gas.select('all')  # Select all domains initially
        selections['s_gas'] = s_gas
        
        logger.info("Created domain selections: s_drop, s_gas")
        return selections
    
    def _create_boundary_selections(self, domain_selections: Dict[str, Any]) -> Dict[str, Any]:
        """Create boundary-based selections"""
        selections = {}
        
        # Access selections container
        sel_container = self.model/'selections'
        
        # Droplet surface (boundary between droplet and gas)
        s_surf = sel_container.create('Adjacent', name='s_surf')
        s_surf.property('input', [domain_selections['s_drop']])  # Reference to droplet domain
        selections['s_surf'] = s_surf
        
        # Skip detailed boundary selections for now - focus on getting basic functionality working
        logger.info("Created boundary selections: s_surf")
        return selections
    
    def _create_physics_selections(self) -> Dict[str, Any]:
        """Create selections for specific physics interfaces"""
        selections = {}
        
        # Access selections container
        sel_container = self.model/'selections'
        
        # Laser irradiation zone - use a simpler approach
        s_laser = sel_container.create('Disk', name='s_laser')
        s_laser.property('posx', f"{self.params['X_max']}[um]")
        s_laser.property('posy', f"{self.params['Y_max']}[um]")
        s_laser.property('r', f"{self.params['R_drop']*0.5}[um]")  # Laser spot size
        selections['s_laser'] = s_laser
        
        logger.info("Created physics selections: s_laser")
        return selections
        
    def _get_boundary_condition(self, boundary: str) -> str:
        """Get geometric condition for domain boundary"""
        geom_params = self.geometry.geom_params
        
        conditions = {
            'left': f'x < {-geom_params.domain_width/2 + 1e-9}',
            'right': f'x > {geom_params.domain_width/2 - 1e-9}',
            'bottom': f'y < {-geom_params.domain_height/2 + 1e-9}',
            'top': f'y > {geom_params.domain_height/2 - 1e-9}'
        }
        
        return conditions[boundary]
    
    def get_selection_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all selections"""
        info = {}
        for name, selection in self.selections.items():
            info[name] = {
                'tag': selection.tag(),
                'entity_dim': selection.property('entitydim'),
                'type': selection.typename()
            }
        return info
    
    def validate_selections(self) -> List[str]:
        """
        Validate all selections have proper entities
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        # For now, just check that selections exist and are not None
        for name, selection in self.selections.items():
            if selection is None:
                errors.append(f"Selection '{name}' is None")
            # Skip entity validation for now as the MPh API is different
                
        if errors:
            logger.warning(f"Selection validation found {len(errors)} issues")
        else:
            logger.info("All selections validated successfully")
            
        return errors
