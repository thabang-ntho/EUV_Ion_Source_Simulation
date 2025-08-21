"""
Study Manager Module

High-level study and solver management using MPh API
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class StudyManager:
        
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
            return meshsing MPh API.
Replaces low-level Java study calls with pythonic study.create() patterns.
"""

from typing import Dict, Any, List, Optional
import logging

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
        
    def create_all_studies(self) -> Dict[str, Any]:
        """
        Create all required studies and meshes
        
        Returns:
            Dictionary of created study objects
        """
        logger.info("Creating studies and meshes with MPh API")
        
        # Create mesh first
        self.meshes['main'] = self._create_mesh()
        
        # Create transient study
        self.studies['transient'] = self._create_transient_study()
        
        # Create steady-state study (if needed)
        if self.params.get('Create_Steady_Study', False):
            self.studies['steady'] = self._create_steady_study()
            
        logger.info(f"Created {len(self.studies)} studies and {len(self.meshes)} meshes")
        return self.studies
    
    def _create_mesh(self) -> Any:
        """Create mesh using MPh API"""
        logger.info("Creating mesh")
        
        # Access meshes container and create mesh
        meshes = self.model/'meshes'
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
    
    def _create_steady_study(self) -> Any:
        """Create steady-state study for initial conditions"""
        logger.info("Creating steady-state study")
        
        # Create study
        study = self.model.studies().create('Study', tag='std2')
        # study.property('name', 'Steady State Analysis')  # Name is set at creation
        
        # Create stationary step
        steady_step = study.create('Stationary', tag='stat1')
        
        # Add only steady-compatible physics
        steady_physics = ['ht']  # Usually only heat transfer for initial conditions
        steady_step.property('physics', steady_physics)
        
        # Solver settings for steady state
        self._configure_steady_solver(study)
        
        logger.info("Created steady-state study")
        return study
    
    def _configure_transient_solver(self, study: Any) -> None:
        """Configure transient solver settings"""
        
        # Create solver configuration
        solver = study.create('SolverConfiguration', tag='sol1')
        # solver.property('name', 'Transient Solver')  # Name is set at creation
        
        # Time stepping method
        time_method = self.params.get('Time_Method', 'bdf')
        solver.property('timemethod', time_method)
        
        # Nonlinear solver
        nonlinear_method = self.params.get('Nonlinear_Method', 'newton')
        solver.property('nonlinmethod', nonlinear_method)
        
        # Tolerances
        rtol = self.params.get('Relative_Tolerance', 1e-3)
        atol = self.params.get('Absolute_Tolerance', 1e-6)
        solver.property('rtol', rtol)
        solver.property('atol', atol)
        
        # Maximum iterations
        max_iter = self.params.get('Max_Iterations', 25)
        solver.property('maxiter', max_iter)
        
        logger.info(f"Configured transient solver: {time_method}, rtol={rtol}, atol={atol}")
    
    def _configure_steady_solver(self, study: Any) -> None:
        """Configure steady-state solver settings"""
        
        # Create solver configuration
        solver = study.create('SolverConfiguration', tag='sol2')
        # solver.property('name', 'Steady Solver')  # Name is set at creation
        
        # Nonlinear solver
        solver.property('nonlinmethod', 'newton')
        
        # Relaxed tolerances for steady state
        solver.property('rtol', 1e-2)
        solver.property('atol', 1e-5)
        solver.property('maxiter', 50)
        
        logger.info("Configured steady-state solver")
    
    def _generate_output_times(self, t_start: float, t_end: float) -> str:
        """Generate logarithmically spaced output times"""
        
        n_outputs = self.params.get('Output_Time_Points', 50)
        
        # Logarithmic spacing
        import numpy as np
        if t_start == 0:
            t_start = t_end / 1000  # Avoid log(0)
            
        times = np.logspace(np.log10(t_start), np.log10(t_end), n_outputs)
        
        # Format as COMSOL expression
        time_str = ' '.join([f'{t:.6e}[s]' for t in times])
        
        logger.info(f"Generated {n_outputs} output times from {t_start:.2e}s to {t_end:.2e}s")
        return time_str
    
    def get_study_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all studies"""
        info = {}
        
        for name, study in self.studies.items():
            steps = []
            for step_tag in study.tags():
                step = study.feature(step_tag)
                steps.append({
                    'tag': step_tag,
                    'type': step.typename(),
                    'physics': step.property('physics') if hasattr(step, 'property') else []
                })
                
            info[name] = {
                'tag': study.tag(),
                'name': study.name(),
                'steps': steps
            }
            
        return info
    
    def validate_studies(self) -> List[str]:
        """
        Validate study configurations
        
        Returns:
            List of validation issues
        """
        issues = []
        
        for name, study in self.studies.items():
            # Check physics assignments
            for step_tag in study.tags():
                step = study.feature(step_tag)
                try:
                    physics_list = step.property('physics')
                    for phys in physics_list:
                        if phys not in self.physics:
                            issues.append(f"Study '{name}' references unknown physics '{phys}'")
                except:
                    pass  # Some steps may not have physics property
                    
        # Check mesh validity
        if 'main' in self.meshes:
            mesh = self.meshes['main']
            # Basic mesh validation would go here
            
        if issues:
            logger.warning(f"Study validation found {len(issues)} issues")
        else:
            logger.info("All studies validated successfully")
            
        return issues
    
    def run_study(self, study_name: str, step_name: Optional[str] = None) -> bool:
        """
        Run a specific study
        
        Args:
            study_name: Name of study to run
            step_name: Specific step to run (optional)
            
        Returns:
            True if successful
        """
        if study_name not in self.studies:
            logger.error(f"Study '{study_name}' not found")
            return False
            
        study = self.studies[study_name]
        
        try:
            if step_name:
                study.run(step_name)
                logger.info(f"Completed study step: {study_name}.{step_name}")
            else:
                study.run()
                logger.info(f"Completed study: {study_name}")
                
            return True
            
        except Exception as e:
            logger.error(f"Study '{study_name}' failed: {e}")
            return False
    
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
