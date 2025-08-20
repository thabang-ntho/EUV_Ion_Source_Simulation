"""
Geometry Builder Module

High-level geometry creation using MPh API.
Replaces low-level java_model.geom() calls with pythonic geometry.create() patterns.
"""

from typing import Dict, Any, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GeometryParams:
    """Geometry parameters extracted from config"""
    domain_width: float
    domain_height: float
    droplet_radius: float
    droplet_center_x: float
    droplet_center_y: float


class GeometryBuilder:
    """High-level geometry builder using MPh API"""
    
    def __init__(self, model, params: Dict[str, Any]):
        """
        Initialize geometry builder
        
        Args:
            model: MPh model object
            params: Parameter dictionary from config
        """
        self.model = model
        self.params = params
        self.geometry = None
        
        # Extract geometry parameters
        self.geom_params = self._extract_geometry_params()
        
    def _extract_geometry_params(self) -> GeometryParams:
        """Extract geometry-specific parameters from config"""
        return GeometryParams(
            domain_width=self.params.get('Domain_Width', 100e-6),
            domain_height=self.params.get('Domain_Height', 100e-6),
            droplet_radius=self.params.get('Droplet_Radius', 25e-6),
            droplet_center_x=self.params.get('Droplet_Center_X', 0.0),
            droplet_center_y=self.params.get('Droplet_Center_Y', 0.0)
        )
    
    def create_domain(self) -> None:
        """
        Create rectangular domain with circular droplet
        
        Uses high-level MPh geometry.create() API instead of Java calls
        """
        logger.info("Creating geometry domain with MPh API")
        
        # Get geometry node from model
        self.geometry = self.model.geometry()
        
        # Create rectangular domain
        domain_rect = self.geometry.create('Rectangle', tag='domain_rect')
        domain_rect.property('width', self.geom_params.domain_width)
        domain_rect.property('height', self.geom_params.domain_height) 
        domain_rect.property('pos', [
            -self.geom_params.domain_width/2,
            -self.geom_params.domain_height/2
        ])
        
        # Create circular droplet
        droplet_circle = self.geometry.create('Circle', tag='droplet_circle')
        droplet_circle.property('r', self.geom_params.droplet_radius)
        droplet_circle.property('pos', [
            self.geom_params.droplet_center_x,
            self.geom_params.droplet_center_y
        ])
        
        # Build geometry
        self.geometry.run()
        
        logger.info(f"Created domain: {self.geom_params.domain_width:.2e} x {self.geom_params.domain_height:.2e}")
        logger.info(f"Created droplet: radius={self.geom_params.droplet_radius:.2e}")
        
    def get_domain_info(self) -> Dict[str, Any]:
        """Get domain geometry information"""
        return {
            'domain_area': self.geom_params.domain_width * self.geom_params.domain_height,
            'droplet_area': 3.14159 * self.geom_params.droplet_radius**2,
            'droplet_center': (self.geom_params.droplet_center_x, self.geom_params.droplet_center_y)
        }
    
    def validate_geometry(self) -> bool:
        """
        Validate geometry constraints
        
        Returns:
            bool: True if geometry is valid
        """
        # Check droplet fits in domain
        max_extent = max(
            abs(self.geom_params.droplet_center_x) + self.geom_params.droplet_radius,
            abs(self.geom_params.droplet_center_y) + self.geom_params.droplet_radius
        )
        
        domain_half_size = min(
            self.geom_params.domain_width / 2,
            self.geom_params.domain_height / 2
        )
        
        if max_extent >= domain_half_size:
            logger.error(f"Droplet extends beyond domain: extent={max_extent:.2e}, domain_half={domain_half_size:.2e}")
            return False
            
        return True
