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
    
    def __init__(self, model, geometry):
        """
        Initialize selection manager
        
        Args:
            model: MPh model object
            geometry: GeometryBuilder instance
        """
        self.model = model
        self.geometry = geometry
        self.selections = {}
        
    def create_all_selections(self) -> Dict[str, Any]:
        """
        Create all required selections for physics assignment
        
        Returns:
            Dict mapping selection names to selection objects
        """
        logger.info("Creating all model selections with MPh API")
        
        # Create domain selections
        self.selections.update(self._create_domain_selections())
        
        # Create boundary selections  
        self.selections.update(self._create_boundary_selections())
        
        # Create special selections for physics
        self.selections.update(self._create_physics_selections())
        
        logger.info(f"Created {len(self.selections)} selections")
        return self.selections
    
    def _create_domain_selections(self) -> Dict[str, Any]:
        """Create domain-based selections"""
        selections = {}
        
        # Get selections container
        try:
            selections_container = self.model/'selections'
        except TypeError:
            # For testing with mocks, fall back to method call
            selections_container = self.model.selections()
        
        # Droplet domain selection
        s_drop = selections_container.create('Disk', name='s_drop')
        # Use geometry parameters for droplet position and radius  
        droplet_x = self.geometry.geom_params.droplet_center_x
        droplet_y = self.geometry.geom_params.droplet_center_y
        droplet_r = self.geometry.geom_params.droplet_radius
        s_drop.property('posx', droplet_x)
        s_drop.property('posy', droplet_y)
        s_drop.property('r', droplet_r)
        selections['s_drop'] = s_drop
        
        # Gas domain selection - select all domains
        s_gas = selections_container.create('Explicit', name='s_gas')
        s_gas.select('all')
        selections['s_gas'] = s_gas
        
        logger.info("Created domain selections: s_drop, s_gas")
        return selections
    
    def _create_boundary_selections(self) -> Dict[str, Any]:
        """Create boundary-based selections"""
        selections = {}
        
        # Get selections container
        try:
            selections_container = self.model/'selections'
        except TypeError:
            # For testing with mocks, fall back to method call
            selections_container = self.model.selections()
        
        # Droplet surface (boundary between droplet and gas)
        s_surf = selections_container.create('Adjacent', name='s_surf')
        s_surf.property('input', [self.selections['s_drop']])
        selections['s_surf'] = s_surf
        
        # Domain boundary selections for boundary conditions
        boundaries = ['left', 'right', 'top', 'bottom']
        for boundary in boundaries:
            s_boundary = selections_container.create('Explicit', name=f's_{boundary}')
            # Use geometric conditions to select domain boundaries
            condition = self._get_boundary_condition(boundary)
            s_boundary.property('condition', condition)
            selections[f's_{boundary}'] = s_boundary
        
        logger.info("Created boundary selections: s_surf, s_left, s_right, s_top, s_bottom")
        return selections
    
    def _create_physics_selections(self) -> Dict[str, Any]:
        """Create selections for specific physics interfaces"""
        selections = {}
        
        # Get selections container
        try:
            selections_container = self.model/'selections'
        except TypeError:
            # For testing with mocks, fall back to method call
            selections_container = self.model.selections()
        
        # Laser heat source selection (part of droplet surface)
        s_laser = selections_container.create('Explicit', name='s_laser')
        s_laser.property('input', [self.selections['s_surf']])
        selections['s_laser'] = s_laser
        
        logger.info("Created physics selections: s_laser")
        return selections
        s_outlet.property('entitydim', 0)
        selections['s_outlet'] = s_outlet
        
        logger.info("Created physics selections: s_laser, s_inlet, s_outlet")
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
        
        for name, selection in self.selections.items():
            try:
                # Check if selection has entities
                entities = selection.entities()
                if len(entities) == 0:
                    errors.append(f"Selection '{name}' has no entities")
            except Exception as e:
                errors.append(f"Selection '{name}' validation failed: {e}")
                
        if errors:
            logger.warning(f"Selection validation found {len(errors)} issues")
        else:
            logger.info("All selections validated successfully")
            
        return errors
