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
        
        # Access meshes container and create mesh
        meshes = self.model/'meshes'
        
        # Check if mesh already exists
        try:
            existing_mesh = meshes/'mesh'
            logger.info("Using existing mesh")
            return existing_mesh
        except:
            # Create new mesh if doesn't exist
            mesh = meshes.create(self.model/'geometries'/'geometry', name='mesh')
            
            # For now, use default meshing - can be refined later
            # COMSOL will automatically generate a suitable mesh
            
            logger.info("Created mesh with default settings")
            return mesh
    
    def _create_transient_study(self) -> Any:
        """Create time-dependent study"""
        logger.info("Creating transient study")
        
        # Access studies container
        studies = self.model/'studies'
        
        # Check if study already exists
        try:
            existing_study = studies/'transient'
            logger.info("Using existing transient study")
            return existing_study
        except:
            # Create new study if doesn't exist
            study = studies.create(name='transient')
            
            # Create time-dependent step
            step = study.create('Transient', name='time_dependent')
            
            # Set time range - for now use simple range
            t_final = self.params.get('Simulation_Time', 1e-6)  # 1 microsecond default
            step.property('tlist', f'range(0, {t_final/100}, {t_final})')  # 100 time steps
            
            # Activate heat transfer physics - simplified for now
            if 'ht' in self.physics:
                logger.info(f"Heat transfer physics tag: {self.physics['ht'].tag()}")
                # For now, skip physics activation to get basic study creation working
                # step.property('activate', [
                #     self.physics['ht'].tag(), 'on',
                #     'frame:spatial1', 'on', 
                #     'frame:material1', 'on',
                # ])
            
            logger.info(f"Created transient study with final time {t_final:.2e}s")
            return study
    
    def _create_solution(self, study) -> Any:
        """Create solution for the study"""
        logger.info("Creating solution")
        
        # Access solutions container
        solutions = self.model/'solutions'
        
        # Check if solution already exists
        try:
            existing_solution = solutions/'solution'
            logger.info("Using existing solution")
            return existing_solution
        except:
            # Create new solution if doesn't exist
            solution = solutions.create(name='solution')
            
            # Link solution to study
            solution.java.study(study.tag())
            solution.java.attach(study.tag())
            
            # Create basic solver components
            solution.create('StudyStep', name='equations')
            solution.create('Variables', name='variables')
            solver = solution.create('Time', name='time_dependent_solver')
            
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
