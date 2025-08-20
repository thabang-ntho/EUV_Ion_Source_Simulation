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
        
        # Create tin material
        tin = self.model.materials().create('Material', tag='tin')
        tin.property('name', 'Tin')
        
        # Basic properties
        tin.property('family', 'metal')
        
        # Density (temperature dependent)
        rho_solid = self.params.get('Tin_Density_Solid', 7310)  # kg/m³
        rho_liquid = self.params.get('Tin_Density_Liquid', 6990)  # kg/m³
        T_melt = self.params.get('Tin_Melting_Temperature', 505.08)  # K
        
        # Use piecewise function for density
        rho_expr = f"if(T<{T_melt}[K], {rho_solid}[kg/m^3], {rho_liquid}[kg/m^3])"
        tin.property('rho', rho_expr)
        
        # Thermal conductivity (temperature dependent)
        k_solid = self.params.get('Tin_Thermal_Conductivity_Solid', 66.8)  # W/(m·K)
        k_liquid = self.params.get('Tin_Thermal_Conductivity_Liquid', 32.0)  # W/(m·K)
        k_expr = f"if(T<{T_melt}[K], {k_solid}[W/(m*K)], {k_liquid}[W/(m*K)])"
        tin.property('k', k_expr)
        
        # Heat capacity (temperature dependent)
        Cp_solid = self.params.get('Tin_Heat_Capacity_Solid', 228)  # J/(kg·K)
        Cp_liquid = self.params.get('Tin_Heat_Capacity_Liquid', 243)  # J/(kg·K)
        Cp_expr = f"if(T<{T_melt}[K], {Cp_solid}[J/(kg*K)], {Cp_liquid}[J/(kg*K)])"
        tin.property('Cp', Cp_expr)
        
        # Viscosity (for liquid phase)
        mu_liquid = self.params.get('Tin_Viscosity_Liquid', 1.85e-3)  # Pa·s
        mu_expr = f"if(T<{T_melt}[K], 1e10[Pa*s], {mu_liquid}[Pa*s])"  # Very high viscosity for solid
        tin.property('mu', mu_expr)
        
        # Latent heat of fusion
        L_fusion = self.params.get('Tin_Latent_Heat_Fusion', 60.2e3)  # J/kg
        tin.property('L_fusion', f'{L_fusion}[J/kg]')
        
        # Surface tension (for interface effects)
        gamma = self.params.get('Tin_Surface_Tension', 0.544)  # N/m
        tin.property('gamma', f'{gamma}[N/m]')
        
        # Optical properties
        absorptivity = self.params.get('Tin_Absorptivity', 0.8)
        tin.property('alpha_abs', f'{absorptivity}')
        
        logger.info("Created tin material with temperature-dependent properties")
        return tin
    
    def _create_gas_material(self, gas_type: str) -> Any:
        """Create gas material based on type"""
        logger.info(f"Creating {gas_type} gas material")
        
        # Create gas material
        gas = self.model.materials().create('Material', tag='gas')
        gas.property('name', f'{gas_type.title()} Gas')
        gas.property('family', 'gas')
        
        if gas_type.lower() == 'argon':
            # Argon properties
            gas.property('rho', '1.784[kg/m^3]')  # At STP
            gas.property('k', '0.01772[W/(m*K)]')
            gas.property('Cp', '520.64[J/(kg*K)]')
            gas.property('mu', '2.125e-5[Pa*s]')
            
        elif gas_type.lower() == 'nitrogen':
            # Nitrogen properties  
            gas.property('rho', '1.251[kg/m^3]')  # At STP
            gas.property('k', '0.02583[W/(m*K)]')
            gas.property('Cp', '1040[J/(kg*K)]')
            gas.property('mu', '1.663e-5[Pa*s]')
            
        elif gas_type.lower() == 'helium':
            # Helium properties
            gas.property('rho', '0.1786[kg/m^3]')  # At STP
            gas.property('k', '0.1513[W/(m*K)]')
            gas.property('Cp', '5193[J/(kg*K)]')
            gas.property('mu', '1.865e-5[Pa*s]')
            
        else:
            logger.warning(f"Unknown gas type: {gas_type}, using default air properties")
            # Air properties as default
            gas.property('rho', '1.293[kg/m^3]')
            gas.property('k', '0.02551[W/(m*K)]')
            gas.property('Cp', '1005[J/(kg*K)]')
            gas.property('mu', '1.716e-5[Pa*s]')
        
        logger.info(f"Created {gas_type} gas material")
        return gas
    
    def assign_materials_to_domains(self, selections: Dict[str, Any]) -> None:
        """Assign materials to geometric domains"""
        logger.info("Assigning materials to domains")
        
        # Assign tin to droplet domain
        if 'tin' in self.materials and 's_drop' in selections:
            self.materials['tin'].property('selection', selections['s_drop'])
            logger.info("Assigned tin material to droplet domain")
            
        # Assign gas to gas domain
        if 'gas' in self.materials and 's_gas' in selections:
            self.materials['gas'].property('selection', selections['s_gas'])
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
        for prop in ['rho', 'k', 'Cp', 'mu']:
            try:
                properties[prop] = material.property(prop)
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
            required_props = ['rho', 'k', 'Cp']
            if name == 'tin':
                required_props.extend(['mu', 'L_fusion'])
                
            for prop in required_props:
                try:
                    value = material.property(prop)
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
                'name': material.property('name'),
                'family': material.property('family'),
                'properties': self.get_material_properties(name)
            }
            
        return info
