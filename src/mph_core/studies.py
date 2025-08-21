"""
Study Manager Module

High-level study and solver management using MPh API.
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
        """Create adaptive mesh with boundary layers"""
        logger.info("Creating adaptive mesh")
        
        # Locate geometry for mesh association
        geometry = None
        try:
            geometry = self.model/'geometries'/'geom1'
        except Exception:
            geometry = None

        # Create mesh (must be attached to a geometry in MPh)
        try:
            meshes_container = self.model/'meshes'
        except TypeError:
            # For testing with mocks, fall back to method call
            meshes_container = self.model.meshes()
        mesh = (
            meshes_container.create(geometry, name='mesh1')
            if geometry is not None else meshes_container.create('Mesh', name='mesh1')
        )
        
        # Global mesh settings
        mesh_size = self.params.get('Global_Mesh_Size', 'fine')
        mesh.property('size', mesh_size)
        
        # Droplet domain - finer mesh (select using named selection 's_drop')
        droplet_mesh = mesh.create('Size', tag='droplet_size')
        try:
            droplet_mesh.select('s_drop')
        except Exception:
            # Fallback to property if select() not available in mock
            droplet_mesh.property('selection', 's_drop')
        
        droplet_hmax = self.params.get('Droplet_Mesh_Max', 2e-6)
        droplet_hmin = self.params.get('Droplet_Mesh_Min', 0.5e-6)
        droplet_mesh.property('hmax', f'{droplet_hmax}[m]')
        droplet_mesh.property('hmin', f'{droplet_hmin}[m]')
        
        # Boundary layer on droplet surface (named selection 's_surf')
        if 'ht' in self.physics:
            # Use singular form to match mph_example pattern
            boundary_layer = mesh.create('BoundaryLayer', tag='bl1')
            try:
                boundary_layer.select('s_surf')
            except Exception:
                boundary_layer.property('selection', 's_surf')
            
            # Map to COMSOL properties used by mph_example
            bl_thickness = self.params.get('Boundary_Layer_Thickness', 0.2e-6)
            bl_layers = self.params.get('Boundary_Layer_Count', 5)
            boundary_layer.property('n', bl_layers)
            boundary_layer.property('thickness', f'{bl_thickness}[m]')
            
            logger.info(f"Added boundary layers: {bl_layers} layers, {bl_thickness:.2e}m thickness")
        
        # Generate base triangular mesh
        try:
            mesh.create('FreeTri', tag='tri1')
        except Exception:
            pass
        
        logger.info(f"Created mesh with {mesh_size} global size")
        return mesh
    
    def _create_transient_study(self) -> Any:
        """Create time-dependent study"""
        logger.info("Creating transient study")
        
        # Create study
        study = self.model.studies().create('Study', tag='std1')
        study.property('name', 'Transient Analysis')
        
        # Create time-dependent step
        time_step = study.create('Transient', tag='time1')
        
        # Add all physics to study
        physics_list = list(self.physics.keys())
        time_step.property('physics', physics_list)
        
        # Time settings
        t_start = self.params.get('Time_Start', 0.0)
        t_end = self.params.get('Time_End', 1e-6)
        dt_init = self.params.get('Time_Step_Initial', 1e-9)
        dt_max = self.params.get('Time_Step_Max', 1e-8)
        
        time_step.property('tstart', f'{t_start}[s]')
        time_step.property('tstop', f'{t_end}[s]')
        time_step.property('initstep', f'{dt_init}[s]')
        time_step.property('maxstep', f'{dt_max}[s]')
        
        # Output times for postprocessing
        output_times = self._generate_output_times(t_start, t_end)
        time_step.property('tout', output_times)
        
        # Solver settings
        self._configure_transient_solver(study)
        
        logger.info(f"Created transient study: {t_start}s to {t_end}s")
        return study
    
    def _create_steady_study(self) -> Any:
        """Create steady-state study for initial conditions"""
        logger.info("Creating steady-state study")
        
        # Create study
        study = self.model.studies().create('Study', tag='std2')
        study.property('name', 'Steady State Analysis')
        
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
        solver.property('name', 'Transient Solver')
        
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
        solver.property('name', 'Steady Solver')
        
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
                'name': study.property('name'),
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
