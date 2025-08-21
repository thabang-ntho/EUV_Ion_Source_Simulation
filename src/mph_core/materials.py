"""
Materials Handler Module

High-level material property management using MPh API.
Replaces low-level Java material calls with pythonic materials.create() patterns.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MaterialsHandler:
    """High-level materials manager using MPh API"""
    
    def __init__(self, model, params: Dict[str, Any]):
        """
        Initialize materials handler
        
        Args:
            model: MPh model object
            params: Parameter dictionary from config
        """
        self.model = model
        self.params = params
        self.materials = {}
        
    def create_all_materials(self) -> Dict[str, Any]:
        """
        Create all required materials
        
        Returns:
            Dictionary of created material objects
        """
        logger.info("Creating all materials with MPh API")
        
        # Create tin material for droplet
        self.materials['tin'] = self._create_tin_material()
        
        # Create gas material (if needed)
        gas_type = self.params.get('Gas_Type', 'none')
        if gas_type != 'none':
            self.materials['gas'] = self._create_gas_material(gas_type)
            
        logger.info(f"Created {len(self.materials)} materials")
        return self.materials
    
    def _create_tin_material(self) -> Any:
        """Create tin material with temperature-dependent properties"""
        logger.info("Creating tin material")

        # Get materials container and create tin material
        try:
            materials_container = self.model/'materials'
        except TypeError:
            # For testing with mocks, fall back to method call
            materials_container = self.model.materials()
        tin = materials_container.create('Common', name='tin')
        
        # Get basic properties section
        try:
            basic = tin/'Basic'
        except TypeError:
            # For testing with mocks, fall back to method call
            basic = tin.Basic()
        
        # Density (use constant values for now, can be made temperature dependent later)
        rho_liquid = self.params.get('rho_sn', '6980[kg/m^3]')
        if isinstance(rho_liquid, str):
            basic.property('density', rho_liquid)
        else:
            basic.property('density', f'{rho_liquid}[kg/m^3]')
        
        # Thermal conductivity
        k_liquid = self.params.get('k_sn', '31[W/(m*K)]')
        if isinstance(k_liquid, str):
            basic.property('thermalconductivity', k_liquid)
        else:
            basic.property('thermalconductivity', f'{k_liquid}[W/(m*K)]')
        
        # Heat capacity
        cp_liquid = self.params.get('Cp_sn', '237[J/(kg*K)]')
        if isinstance(cp_liquid, str):
            basic.property('heatcapacity', cp_liquid)
        else:
            basic.property('heatcapacity', f'{cp_liquid}[J/(kg*K)]')
        
        # Dynamic viscosity (for flow physics)
        mu_liquid = self.params.get('mu_sn', '1.8e-3[Pa*s]')
        if isinstance(mu_liquid, str):
            basic.property('dynamicviscosity', mu_liquid)
        else:
            basic.property('dynamicviscosity', f'{mu_liquid}[Pa*s]')
        
        logger.info("Created tin material with basic properties")
        return tin
        
    def _create_gas_material(self) -> Any:
        """Create gas material (air) with basic properties"""
        logger.info("Creating gas material")

        # Get materials container and create gas material
        try:
            materials_container = self.model/'materials'
        except TypeError:
            # For testing with mocks, fall back to method call
            materials_container = self.model.materials()
        gas = materials_container.create('Common', name='gas')
        
        # Get basic properties section
        try:
            basic = gas/'Basic'
        except TypeError:
            # For testing with mocks, fall back to method call
            basic = gas.Basic()
    
    def assign_materials_to_domains(self, selections: Dict[str, Any]) -> None:
        """Assign materials to geometric domains"""
        logger.info("Assigning materials to domains")
        
        # Assign tin to droplet domain
        if 'tin' in self.materials and 's_drop' in selections:
            self.materials['tin'].select(selections['s_drop'])
            logger.info("Assigned tin material to droplet domain")
            
        # Assign gas to gas domain (if gas material exists)
        if 'gas' in self.materials and 's_gas' in selections:
            self.materials['gas'].select(selections['s_gas'])
            logger.info("Assigned gas material to gas domain")
    
    def get_material_properties(self, material_name: str) -> Dict[str, str]:
        """
        Get material property expressions
        
        Args:
            material_name: Name of material ('tin' or 'gas')
            
        Returns:
            Dictionary of property expressions
        """
        if material_name not in self.materials:
            logger.error(f"Material '{material_name}' not found")
            return {}
            
        material = self.materials[material_name]
        
        properties = {}
        for prop in ['density', 'thermalconductivity', 'heatcapacity', 'dynamicviscosity']:
            try:
                try:
                    basic = material/'Basic'
                except TypeError:
                    # For testing with mocks, fall back to method call
                    basic = material.Basic()
                properties[prop] = basic.property(prop)
            except:
                properties[prop] = 'undefined'
                
        return properties
    
    def validate_materials(self) -> Dict[str, bool]:
        """
        Validate material property definitions
        
        Returns:
            Dictionary mapping material names to validation status
        """
        validation = {}
        
        for name, material in self.materials.items():
            is_valid = True
            
            # Check required properties exist
            required_props = ['density', 'thermalconductivity', 'heatcapacity']
            if name == 'tin':
                required_props.append('dynamicviscosity')
                
            for prop in required_props:
                try:
                    try:
                        basic = material/'Basic'
                    except TypeError:
                        # For testing with mocks, fall back to method call
                        basic = material.Basic()
                    value = basic.property(prop)
                    if not value or value == '':
                        is_valid = False
                        logger.error(f"Material '{name}' missing property '{prop}'")
                except:
                    is_valid = False
                    logger.error(f"Material '{name}' property '{prop}' not accessible")
                    
            validation[name] = is_valid
            
        if all(validation.values()):
            logger.info("All materials validated successfully")
        else:
            failed = [name for name, valid in validation.items() if not valid]
            logger.warning(f"Material validation failed for: {failed}")
            
        return validation
    
    def get_material_info(self) -> Dict[str, Dict[str, Any]]:
        """Get summary information about all materials"""
        info = {}
        
        for name, material in self.materials.items():
            info[name] = {
                'tag': material.tag(),
                'properties': self.get_material_properties(name)
            }
            
        return info
