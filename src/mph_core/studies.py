"""
Study Manager Module

High-level study and solver management using MPh API
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class StudyManager:
    """High-level study manager using MPh API"""
    
    def __init__(self, model, physics_interfaces: Dict[str, Any], params: Dict[str, Any]):
        """
        Initialize study manager
        
        Args:
            model: MPh model object
            physics_interfaces: Dictionary of physics interfaces
            params: Parameter dictionary from config
        """
        self.model = model
        self.physics = physics_interfaces
        self.params = params
        self.studies = {}
        self.meshes = {}
        
    def _create_mesh(self) -> Any:
        """Create mesh for the geometry"""
        logger.info("Creating mesh")
        
        # Access meshes container and create mesh directly
        meshes = self.model/'meshes'
        mesh = meshes.create(self.model/'geometries'/'geometry', name='mesh')
        
        # For now, use default meshing - can be refined later
        # COMSOL will automatically generate a suitable mesh
        
        logger.info("Created mesh with default settings")
        return mesh
    
    def _create_transient_study(self) -> Any:
        """Create time-dependent study"""
        logger.info("Creating transient study")
        
        # Access studies container and create study directly
        studies = self.model/'studies'
        study = studies.create(name='transient')
        
        # Set study properties 
        study.java.setGenPlots(False)
        study.java.setGenConv(False)
        
        # Create time-dependent step
        step = study.create('Transient', name='time_dependent')
        
        # Set time range - for now use simple range
        t_final = self.params.get('Simulation_Time', 1e-6)  # 1 microsecond default
        step.property('tlist', f'range(0, {t_final/100}, {t_final})')  # 100 time steps
        
        logger.info(f"Physics interfaces available: {list(self.physics.keys())}")

        # Activate physics per mph_example.py using explicit node references
        # Build the activation list as alternating references and states
        try:
            physics_container = self.model/'physics'
            activation_list = []

            # Prefer explicit Heat Transfer interface created by PhysicsManager
            # PhysicsManager names it 'heat_transfer'; if missing, fall back to any provided 'ht' reference
            iface_node = None
            try:
                iface_node = physics_container/'heat_transfer'
            except Exception:
                pass
            if iface_node is None and 'ht' in self.physics:
                # The property API accepts node references; use the object from manager
                iface_node = self.physics['ht']

            if iface_node is not None:
                try:
                    logger.info(f"Activating physics interface: tag={iface_node.tag()} path={getattr(iface_node, 'path', lambda: 'n/a')() if hasattr(iface_node, 'path') else 'n/a'}")
                except Exception:
                    pass
                activation_list.extend([iface_node, 'on'])
            else:
                logger.warning("No heat transfer interface found to activate; continuing without explicit activation")

            # Frames as seen in mph_example.py; discover robustly
            try:
                frames = self.model/'frames'
                spatial = None
                material = None
                # Try common tags first
                try:
                    spatial = frames/'spatial1'
                except Exception:
                    pass
                try:
                    material = frames/'material1'
                except Exception:
                    pass
                # Fallback: search by name pattern
                if (spatial is None or material is None) and frames:
                    for fr in frames:
                        try:
                            tg = fr.tag()
                            if spatial is None and tg.startswith('spatial'):
                                spatial = fr
                            if material is None and tg.startswith('material'):
                                material = fr
                        except Exception:
                            continue
                if spatial is not None:
                    activation_list.extend([f"frame:{spatial.tag()}", 'on'])
                if material is not None:
                    activation_list.extend([f"frame:{material.tag()}", 'on'])
                if spatial is None or material is None:
                    # As a last resort, use default names
                    activation_list.extend(['frame:spatial1', 'on', 'frame:material1', 'on'])
            except Exception:
                activation_list.extend(['frame:spatial1', 'on', 'frame:material1', 'on'])

            # Debug types for clarity
            try:
                debug_types = [type(x).__name__ for x in activation_list]
                logger.debug(f"Activation types: {debug_types}")
            except Exception:
                pass

            if activation_list:
                try:
                    step.property('activate', activation_list)
                except Exception as e1:
                    # Fallback: convert any node references to their path strings
                    try:
                        converted: List[str] = []
                        for item in activation_list:
                            if hasattr(item, 'path'):
                                converted.append(item.path())
                            else:
                                converted.append(item)
                        logger.debug(f"Fallback activation payload (as strings): {converted}")
                        step.property('activate', converted)
                    except Exception as e2:
                        raise e1
        except Exception as e:
            # Log but do not fail study creation; helps when running in --check-only environments
            logger.warning(f"Physics activation setup skipped due to error: {e}")
        
        logger.info(f"Created transient study with final time {t_final:.2e}s")
        return study

    # --- Additions: API expected by ModelBuilder ---
    def create_all_studies(self) -> Dict[str, Any]:
        """Create required mesh and transient study, return studies dict."""
        logger.info("Creating studies and meshes with MPh API")
        self.meshes['main'] = self._create_mesh()
        self.studies['transient'] = self._create_transient_study()
        return self.studies

    def validate_studies(self) -> List[str]:
        """Basic validation of created studies; returns list of issues."""
        issues: List[str] = []
        if 'transient' not in self.studies:
            issues.append("Missing 'transient' study")
        return issues

    def run_study(self, study_name: str, step_name: Optional[str] = None) -> bool:
        """Run a study by name; create solution if missing and attach.

        Returns True on apparent success (no exception), False otherwise.
        """
        try:
            studies = self.model/'studies'
            study = studies[study_name]
            # Ensure a solution exists and is attached
            solutions = self.model/'solutions'
            try:
                solution = solutions/'solution'
            except Exception:
                solution = solutions.create(name='solution')
                solution.java.study(study.tag())
                solution.java.attach(study.tag())
                solution.create('StudyStep', name='equations')
                solution.create('Variables', name='variables')
                solver = solution.create('Time', name='time_dependent_solver')
                try:
                    t_final = self.params.get('Simulation_Time', 1e-6)
                    solver.property('tlist', f'range(0, {t_final/100}, {t_final})')
                except Exception:
                    pass
            # Solve the study
            study.solve()
            return True
        except Exception as e:
            logger.error(f"Failed to run study '{study_name}': {e}")
            return False

    def get_study_info(self) -> Dict[str, Dict[str, Any]]:
        """Return minimal info about created studies."""
        info: Dict[str, Dict[str, Any]] = {}
        for name, study in self.studies.items():
            try:
                info[name] = {"tag": study.tag(), "name": study.name()}
            except Exception:
                info[name] = {"tag": None, "name": None}
        return info
    
    def _create_solution(self, study) -> Any:
        """Create solution for the study"""
        logger.info("Creating solution")
        
        # Access solutions container and create solution directly
        solutions = self.model/'solutions'
        solution = solutions.create(name='solution')
        
        # Link solution to study - this sets the solution to use this study
        solution.java.study(study.tag())
        solution.java.attach(study.tag())
        
        # Create basic solver components
        solution.create('StudyStep', name='equations')
        variables = solution.create('Variables', name='variables')
        
        # Set time list for variables
        t_final = self.params.get('Simulation_Time', 1e-6)  # 1 microsecond default
        variables.property('clist', [f'range(0, {t_final/100}, {t_final})', '0.001[s]'])
        
        # Create time-dependent solver
        solver = solution.create('Time', name='time_dependent_solver')
        solver.property('tlist', f'range(0, {t_final/100}, {t_final})')
        
        # The "No current feature assigned" error suggests we need this
        # Looking at other examples, we don't need to set a feature explicitly
        # Just making sure all components are properly created and linked
        
        logger.info("Created solution and linked to study")
        return solution
    
    def create_study_and_solve(self) -> Any:
        """Create study, mesh geometry, and set up for solving"""
        try:
            logger.info("Starting complete study creation and setup")
            
            # Create mesh
            mesh = self._create_mesh()
            
            # Create study (using new _create_study method)
            study = self._create_study()
            
            # Create solution
            solution = self._create_solution(study)
            
            logger.info("Study creation and setup completed successfully")
            return {
                'mesh': mesh,
                'study': study,
                'solution': solution
            }
            
        except Exception as e:
            logger.error(f"Failed to create study and setup: {e}")
            raise
    
    def _create_study(self) -> Any:
        """Create transient study (wrapper for backwards compatibility)"""
        return self._create_transient_study()
    
    def solve(self, study_name: str = 'transient') -> Any:
        """Solve the study"""
        try:
            logger.info(f"Starting solution for study: {study_name}")
            
            # Find the study
            studies = self.model/'studies'
            study = studies[study_name]
            
            # Run the study
            study.solve()
            
            logger.info(f"Successfully solved study: {study_name}")
            return study
            
        except Exception as e:
            logger.error(f"Failed to solve study {study_name}: {e}")
            raise
