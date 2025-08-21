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
    
    def create_geometry(self, model) -> None:
        """Create 2D droplet geometry using MPh API"""
        logger.info("Creating 2D droplet geometry")
        
        # Access geometries container and create a 2D geometry
        geometries = model/'geometries'
        self.geometry = geometries.create(2, name='geometry')
        
        # Get parameters from config with fallbacks
        Lx = self.params.get('Lx', 2.0e-4)  # Domain width
        Ly = self.params.get('Ly', 3.0e-4)  # Domain height
        R = self.params.get('R', 1.35e-5)   # Droplet radius
        x_center = self.params.get('x_beam', Lx/2)  # Droplet center x
        y_center = self.params.get('y_beam', Ly/2)  # Droplet center y
        
        # Create domain rectangle
        domain = self.geometry.create('Rectangle', name='domain')
        domain.property('size', [f"{Lx*1e6}[um]", f"{Ly*1e6}[um]"])
        domain.property('pos', ['0', '0'])
        
        # Create droplet circle
        droplet = self.geometry.create('Circle', name='droplet')
        droplet.property('r', f"{R*1e6}[um]")
        droplet.property('pos', [f"{x_center*1e6}[um]", f"{y_center*1e6}[um]"])
        
        # Build geometry
        model.build(self.geometry)
        logger.info("Geometry built successfully")
    
    def create_mesh(self, model) -> None:
        """Create mesh using MPh API"""
        logger.info("Creating mesh")
        
        # Access mesh container
        meshes = model/'meshes'
        mesh = meshes.create(self.geometry, name='mesh')
        
        # Configure mesh size
        size = mesh.create('Size', name='size')
        size.property('hauto', 3)  # Finer mesh
        
        # Build mesh
        model.build(mesh)
        logger.info("Mesh created successfully")
        
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
