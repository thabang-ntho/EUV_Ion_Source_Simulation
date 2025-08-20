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
        
        # Droplet domain selection
        s_drop = self.model.selections().create('Disk', tag='s_drop')
        s_drop.property('entitydim', 2)  # Domain selection
        s_drop.property('condition', 'circle_droplet')
        selections['s_drop'] = s_drop
        
        # Gas domain selection (complement of droplet)
        s_gas = self.model.selections().create('Complement', tag='s_gas')
        s_gas.property('entitydim', 2)
        s_gas.property('input', ['s_drop'])
        selections['s_gas'] = s_gas
        
        logger.info("Created domain selections: s_drop, s_gas")
        return selections
    
    def _create_boundary_selections(self) -> Dict[str, Any]:
        """Create boundary-based selections"""
        selections = {}
        
        # Droplet surface (boundary between droplet and gas)
        s_surf = self.model.selections().create('Adjacent', tag='s_surf')
        s_surf.property('entitydim', 1)  # Boundary selection
        s_surf.property('input', ['s_drop'])
        selections['s_surf'] = s_surf
        
        # Domain boundaries
        boundaries = ['left', 'right', 'top', 'bottom']
        for boundary in boundaries:
            sel = self.model.selections().create('Box', tag=f's_{boundary}')
            sel.property('entitydim', 1)
            sel.property('condition', self._get_boundary_condition(boundary))
            selections[f's_{boundary}'] = sel
            
        logger.info(f"Created boundary selections: s_surf, {', '.join(f's_{b}' for b in boundaries)}")
        return selections
    
    def _create_physics_selections(self) -> Dict[str, Any]:
        """Create selections for specific physics interfaces"""
        selections = {}
        
        # Laser irradiation zone (subset of droplet surface)
        s_laser = self.model.selections().create('Disk', tag='s_laser')
        s_laser.property('entitydim', 1)
        s_laser.property('condition', 'laser_zone')  # Will be refined based on variant
        selections['s_laser'] = s_laser
        
        # Fluid boundary conditions
        s_inlet = self.model.selections().create('Point', tag='s_inlet')
        s_inlet.property('entitydim', 0)  # Point selection
        selections['s_inlet'] = s_inlet
        
        s_outlet = self.model.selections().create('Point', tag='s_outlet')
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
