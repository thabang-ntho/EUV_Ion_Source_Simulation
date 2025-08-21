"""
Model Builder Module

Main orchestrator for MPh-based COMSOL model building.
Replaces the old build.py with high-level MPh API architecture.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import mph

from .geometry import GeometryBuilder
from .selections import SelectionManager
from .physics import PhysicsManager
from .materials import MaterialsHandler
from .studies import StudyManager
from .postprocess import ResultsProcessor

logger = logging.getLogger(__name__)


class ModelBuilder:
    """
    High-level model builder using MPh API
    
    This is the main entry point for building COMSOL models with the new
    MPh-based architecture. It orchestrates all the specialized builders.
    """
    
    def __init__(self, params: Dict[str, Any], variant: str = 'fresnel'):
        """
        Initialize model builder
        
        Args:
            params: Parameter dictionary from config
            variant: Model variant ('fresnel' or 'kumar')
        """
        self.params = params
        self.variant = variant
        self.model = None
        
        # Component builders
        self.geometry_builder = None
        self.selection_manager = None
        self.physics_manager = None
        self.materials_handler = None
        self.study_manager = None
        self.results_processor = None
        
        # Build status tracking
        self.build_stages = {
            'client_connected': False,
            'model_created': False,
            'parameters_set': False,
            'geometry_built': False,
            'selections_created': False,
            'materials_assigned': False,
            'physics_setup': False,
            'studies_created': False,
            'solved': False,
            'results_extracted': False
        }
        
    def build_complete_model(self, output_path: Optional[Path] = None) -> Path:
        """
        Build complete model from scratch
        
        Args:
            output_path: Path for saving .mph file (optional)
            
        Returns:
            Path to saved .mph file
        """
        logger.info(f"Building complete {self.variant} model with MPh API")
        
        try:
            # Stage 1: Initialize COMSOL connection
            self._connect_to_comsol()
            
            # Stage 2: Create model and set parameters
            self._create_model()
            self._set_parameters()
            
            # Stage 3: Build geometry and selections
            self._build_geometry()
            self._create_selections()
            
            # Stage 4: Setup materials and physics
            self._setup_materials()
            self._setup_physics()
            
            # Stage 5: Create studies and mesh
            self._create_studies()
            
            # Stage 6: Save model
            output_file = self._save_model(output_path)
            
            logger.info(f"Successfully built {self.variant} model: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Model building failed at stage {self._get_current_stage()}: {e}")
            raise
            
    def solve_and_extract_results(self, study_name: str = 'transient') -> Dict[str, Path]:
        """
        Solve model and extract all results
        
        Args:
            study_name: Name of study to solve
            
        Returns:
            Dictionary of extracted result file paths
        """
        logger.info(f"Solving {study_name} study and extracting results")
        
        try:
            # Solve the study
            if not self.study_manager.run_study(study_name):
                raise RuntimeError(f"Study '{study_name}' failed to solve")
                
            self.build_stages['solved'] = True
            
            # Extract results
            self.results_processor = ResultsProcessor(self.model, self.params)
            results = self.results_processor.extract_all_results(self.variant)
            
            self.build_stages['results_extracted'] = True
            
            logger.info(f"Successfully solved and extracted {len(results)} result files")
            return results
            
        except Exception as e:
            logger.error(f"Solving/extraction failed: {e}")
            raise
    
    def _connect_to_comsol(self) -> None:
        """Connect to COMSOL Multiphysics"""
        logger.info("Connecting to COMSOL Multiphysics")

        try:
            # Initialize MPh client
            import os
            host = os.environ.get("COMSOL_HOST")
            port = os.environ.get("COMSOL_PORT")
            cores = os.environ.get("COMSOL_CORES")
            if host and port:
                self.client = mph.start(host=host, port=int(port))
            elif cores:
                # Some mph versions accept cores kwarg
                try:
                    self.client = mph.start(cores=int(cores))
                except TypeError:
                    # Fallback if cores kw unsupported
                    self.client = mph.start()
            else:
                self.client = mph.start()
            self.build_stages['client_connected'] = True
            
            logger.info("Successfully connected to COMSOL")
            
        except Exception as e:
            logger.error(f"Failed to connect to COMSOL: {e}")
            raise
    
    def _create_model(self) -> None:
        """Create new model with appropriate settings"""
        logger.info(f"Creating new {self.variant} model")

        # Create model
        model_name = f"EUV_Droplet_{self.variant.title()}"
        self.model = self.client.create(model_name)

        # Model is created, no need to set name property as it's already set
        logger.info(f"Model '{model_name}' created successfully")

        # Ensure a component exists (per mph_example.py) so frames are present
        try:
            components = self.model/'components'
            # If a default component exists, access won't throw; otherwise create one
            try:
                _ = components/'component'
                logger.info("Using existing component")
            except Exception:
                components.create(True, name='component')
                logger.info("Created component 'component'")
        except Exception as e:
            logger.warning(f"Unable to ensure component presence: {e}")

        # Set geometry space dimension (handled by geometry builder)

        self.build_stages['model_created'] = True
        logger.info(f"Created model: {model_name}")
    
    def _set_parameters(self) -> None:
        """Set all model parameters from config"""
        logger.info("Setting model parameters")
        
        param_count = 0
        for name, value in self.params.items():
            try:
                # Convert to COMSOL parameter format
                if isinstance(value, (int, float)):
                    param_value = str(value)
                elif isinstance(value, str):
                    param_value = value
                else:
                    continue  # Skip non-numeric/string parameters
                    
                self.model.parameter(name, param_value)
                param_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to set parameter '{name}': {e}")
        
        self.build_stages['parameters_set'] = True
        logger.info(f"Set {param_count} model parameters")
    
    def _build_geometry(self) -> None:
        """Build model geometry"""
        logger.info("Building geometry")
        
        self.geometry_builder = GeometryBuilder(self.model, self.params)
        
        # Validate geometry parameters
        if not self.geometry_builder.validate_geometry():
            raise ValueError("Invalid geometry parameters")
            
        # Create geometry
        self.geometry_builder.create_geometry(self.model)
        
        self.build_stages['geometry_built'] = True
        logger.info("Geometry built successfully")
    
    def _create_selections(self) -> None:
        """Create named selections"""
        logger.info("Creating selections")
        
        self.selection_manager = SelectionManager(self.model, self.geometry_builder, self.params)
        
        # Create all selections
        selections = self.selection_manager.create_all_selections()
        
        # Validate selections
        errors = self.selection_manager.validate_selections()
        if errors:
            raise ValueError(f"Selection validation failed: {errors}")
            
        self.build_stages['selections_created'] = True
        logger.info(f"Created {len(selections)} selections")
    
    def _setup_materials(self) -> None:
        """Setup materials"""
        logger.info("Setting up materials")
        
        self.materials_handler = MaterialsHandler(self.model, self.params)
        
        # Create materials
        materials = self.materials_handler.create_all_materials()
        
        # Assign to domains
        self.materials_handler.assign_materials_to_domains(
            self.selection_manager.selections
        )
        
        # Validate materials
        validation = self.materials_handler.validate_materials()
        if not all(validation.values()):
            failed = [name for name, valid in validation.items() if not valid]
            raise ValueError(f"Material validation failed for: {failed}")
            
        self.build_stages['materials_assigned'] = True
        logger.info(f"Setup {len(materials)} materials")
    
    def _setup_physics(self) -> None:
        """Setup physics interfaces"""
        logger.info("Setting up physics")
        
        self.physics_manager = PhysicsManager(
            self.model,
            self.selection_manager.selections,
            self.materials_handler.materials
        )
        
        # Setup physics for variant
        physics_interfaces = self.physics_manager.setup_all_physics(self.variant)
        
        # Validate physics coupling
        issues = self.physics_manager.validate_physics_coupling()
        if issues:
            logger.warning(f"Physics validation issues: {issues}")
            
        self.build_stages['physics_setup'] = True
        logger.info(f"Setup {len(physics_interfaces)} physics interfaces")
    
    def _create_studies(self) -> None:
        """Create studies and mesh"""
        logger.info("Creating studies and mesh")
        
        self.study_manager = StudyManager(
            self.model,
            self.physics_manager.physics_interfaces,
            self.params
        )
        
        # Create studies
        studies = self.study_manager.create_all_studies()
        
        # Validate studies
        issues = self.study_manager.validate_studies()
        if issues:
            logger.warning(f"Study validation issues: {issues}")
            
        self.build_stages['studies_created'] = True
        logger.info(f"Created {len(studies)} studies")
    
    def _save_model(self, output_path: Optional[Path] = None) -> Path:
        """Save model to .mph file"""
        
        if output_path is None:
            output_dir = Path(self.params.get('Output_Directory', 'results'))
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{self.variant}_model.mph"
        
        logger.info(f"Saving model to {output_path}")
        
        try:
            self.model.save(str(output_path))
            logger.info(f"Successfully saved model: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
    
    def _get_current_stage(self) -> str:
        """Get current build stage for error reporting"""
        for stage, completed in self.build_stages.items():
            if not completed:
                return stage
        return "completed"
    
    def get_build_status(self) -> Dict[str, bool]:
        """Get current build status"""
        return self.build_stages.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        info = {
            'variant': self.variant,
            'build_status': self.get_build_status(),
            'model_name': self.model.name() if self.model else None
        }
        
        # Add component info if available
        if self.geometry_builder:
            info['geometry'] = self.geometry_builder.get_domain_info()
            
        if self.selection_manager:
            info['selections'] = self.selection_manager.get_selection_info()
            
        if self.materials_handler:
            info['materials'] = self.materials_handler.get_material_info()
            
        if self.physics_manager:
            info['physics'] = self.physics_manager.get_physics_info()
            
        if self.study_manager:
            info['studies'] = self.study_manager.get_study_info()
            
        return info
    
    def cleanup(self) -> None:
        """Clean up COMSOL connection"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.disconnect()
                logger.info("Disconnected from COMSOL")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
        
        if exc_type is not None:
            logger.error(f"Exception in model builder: {exc_val}")
        
        return False  # Don't suppress exceptions
