"""
MPh-based CLI Entry Point

New CLI entry point for the MPh-based implementation.
Provides backward compatibility while transitioning to new architecture.
"""

import argparse
import sys
from pathlib import Path
import logging
from typing import Dict, Any, Optional

# New MPh-based imports
from .mph_core.model_builder import ModelBuilder
from .models.mph_fresnel import FresnelModelBuilder
from .models.mph_kumar import KumarModelBuilder

# Existing core imports (for config loading)
from .core.config.loader import load_config
from .core.errors import ConfigError, SimError

logger = logging.getLogger(__name__)


class MPhCLI:
    """Command-line interface for MPh-based model building"""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser"""
        
        parser = argparse.ArgumentParser(
            description="EUV Droplet Simulation - MPh API Implementation",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s fresnel --config global_parameters_pp_v2.txt --solve
  %(prog)s kumar --config data/laser_parameters_pp_v2.txt --output kumar_model.mph
  %(prog)s fresnel --list-params
  %(prog)s --validate-config data/global_parameters_pp_v2.txt
            """
        )
        
        # Variant selection (required)
        subparsers = parser.add_subparsers(dest='variant', help='Model variant')
        subparsers.required = True
        
        # Fresnel variant
        fresnel_parser = subparsers.add_parser('fresnel', help='Fresnel evaporation model')
        self._add_common_arguments(fresnel_parser)
        self._add_fresnel_arguments(fresnel_parser)
        
        # Kumar variant
        kumar_parser = subparsers.add_parser('kumar', help='Kumar fluid dynamics model')
        self._add_common_arguments(kumar_parser)
        self._add_kumar_arguments(kumar_parser)
        
        # Utility commands
        parser.add_argument('--validate-config', metavar='CONFIG_FILE',
                          help='Validate configuration file and exit')
        parser.add_argument('--list-defaults', action='store_true',
                          help='List default parameters for variant and exit')
        parser.add_argument('--version', action='version', version='MPh Implementation v1.0')
        
        return parser
    
    def _add_common_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add common arguments to variant parsers"""
        
        # Configuration
        parser.add_argument('-c', '--config', metavar='CONFIG_FILE',
                          help='Configuration file path (default: auto-detect)')
        parser.add_argument('-p', '--param', action='append', metavar='KEY=VALUE',
                          help='Override parameter (can be used multiple times)')
        
        # Output control
        parser.add_argument('-o', '--output', metavar='OUTPUT_FILE',
                          help='Output .mph file path (default: auto-generate)')
        parser.add_argument('--output-dir', metavar='DIR', default='results',
                          help='Output directory (default: results)')
        
        # Execution control
        parser.add_argument('--build-only', action='store_true',
                          help='Build model without solving')
        parser.add_argument('--solve', action='store_true',
                          help='Solve model after building')
        parser.add_argument('--extract-results', action='store_true',
                          help='Extract results after solving')
        
        # Logging
        parser.add_argument('-v', '--verbose', action='count', default=0,
                          help='Increase verbosity (use -v, -vv, -vvv)')
        parser.add_argument('--log-file', metavar='LOG_FILE',
                          help='Log file path (default: console only)')
        
        # Development/debugging
        parser.add_argument('--dry-run', action='store_true',
                          help='Show what would be done without executing')
        parser.add_argument('--validate-only', action='store_true',
                          help='Validate parameters and geometry only')
        parser.add_argument('--list-params', action='store_true',
                          help='List all parameters and exit')
        
    def _add_fresnel_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add Fresnel-specific arguments"""
        
        fresnel_group = parser.add_argument_group('Fresnel-specific options')
        
        fresnel_group.add_argument('--laser-power', type=float, metavar='POWER',
                                 help='Laser power (W/m²)')
        fresnel_group.add_argument('--laser-spot-radius', type=float, metavar='RADIUS',
                                 help='Laser spot radius (m)')
        fresnel_group.add_argument('--gas-type', choices=['argon', 'nitrogen', 'helium'],
                                 help='Background gas type')
        fresnel_group.add_argument('--evaporation-coeff', type=float, metavar='COEFF',
                                 help='Evaporation coefficient')
        
    def _add_kumar_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add Kumar-specific arguments"""
        
        kumar_group = parser.add_argument_group('Kumar-specific options')
        
        kumar_group.add_argument('--volumetric-heating', type=float, metavar='POWER',
                               help='Volumetric heat generation (W/m³)')
        kumar_group.add_argument('--reynolds-number', type=float, metavar='RE',
                               help='Reynolds number')
        kumar_group.add_argument('--weber-number', type=float, metavar='WE',
                               help='Weber number')
        kumar_group.add_argument('--enable-marangoni', action='store_true',
                               help='Enable Marangoni effect')
        kumar_group.add_argument('--disable-marangoni', action='store_true',
                               help='Disable Marangoni effect')
    
    def run(self, args: Optional[list] = None) -> int:
        """Run CLI with given arguments"""
        
        parsed_args = self.parser.parse_args(args)
        
        try:
            # Setup logging
            log_level = self._get_log_level(parsed_args.verbose)
            self._setup_logging(level=log_level, log_file=getattr(parsed_args, 'log_file', None))
            
            # Handle utility commands
            if hasattr(parsed_args, 'validate_config') and parsed_args.validate_config:
                return self._validate_config(parsed_args.validate_config)
            
            if parsed_args.list_defaults:
                return self._list_defaults(parsed_args.variant)
            
            # Load configuration
            config_path = self._find_config_file(getattr(parsed_args, 'config', None))
            params = load_config(config_path) if config_path else {}
            
            # Apply parameter overrides
            if hasattr(parsed_args, 'param') and parsed_args.param:
                params.update(self._parse_param_overrides(parsed_args.param))
            
            # Apply CLI-specific parameters
            params.update(self._extract_variant_params(parsed_args))
            
            # Set output directory
            params['Output_Directory'] = parsed_args.output_dir
            
            # Handle list parameters
            if getattr(parsed_args, 'list_params', False):
                return self._list_parameters(params, parsed_args.variant)
            
            # Dry run
            if parsed_args.dry_run:
                return self._dry_run(params, parsed_args)
            
            # Validation only
            if parsed_args.validate_only:
                return self._validate_only(params, parsed_args.variant)
            
            # Build and optionally solve model
            return self._build_model(params, parsed_args)
            
        except ConfigError as e:
            logger.error(f"Configuration error: {e}")
            return 1
        except SimError as e:
            logger.error(f"Simulation error: {e}")
            return 2
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 3
    
    def _get_log_level(self, verbose_count: int) -> int:
        """Convert verbose count to log level"""
        levels = [logging.WARNING, logging.INFO, logging.DEBUG]
        return levels[min(verbose_count, len(levels) - 1)]
    
    def _setup_logging(self, level: int = logging.INFO, log_file: Optional[str] = None) -> None:
        """Setup logging configuration"""
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        handlers.append(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always debug level for file
            handlers.append(file_handler)
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True
        )
    
    def _find_config_file(self, config_path: Optional[str]) -> Optional[Path]:
        """Find configuration file"""
        if config_path:
            path = Path(config_path)
            if not path.exists():
                raise ConfigError(f"Config file not found: {config_path}")
            return path
        
        # Auto-detect config files
        candidates = [
            'data/global_parameters_pp_v2.txt',
            'src/global_parameters_pp_v2.txt',
            'global_parameters_pp_v2.txt'
        ]
        
        for candidate in candidates:
            path = Path(candidate)
            if path.exists():
                logger.info(f"Auto-detected config file: {path}")
                return path
        
        logger.warning("No config file found, using defaults")
        return None
    
    def _parse_param_overrides(self, param_overrides: list) -> Dict[str, Any]:
        """Parse parameter overrides from command line"""
        params = {}
        
        for override in param_overrides:
            if '=' not in override:
                raise ConfigError(f"Invalid parameter format: {override}")
            
            key, value = override.split('=', 1)
            
            # Try to convert to appropriate type
            try:
                if '.' in value or 'e' in value.lower():
                    params[key] = float(value)
                elif value.isdigit():
                    params[key] = int(value)
                elif value.lower() in ('true', 'false'):
                    params[key] = value.lower() == 'true'
                else:
                    params[key] = value
            except ValueError:
                params[key] = value  # Keep as string
        
        return params
    
    def _extract_variant_params(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Extract variant-specific parameters from CLI args"""
        params = {}
        
        if args.variant == 'fresnel':
            if hasattr(args, 'laser_power') and args.laser_power is not None:
                params['Laser_Power'] = args.laser_power
            if hasattr(args, 'laser_spot_radius') and args.laser_spot_radius is not None:
                params['Laser_Spot_Radius'] = args.laser_spot_radius
            if hasattr(args, 'gas_type') and args.gas_type is not None:
                params['Gas_Type'] = args.gas_type
            if hasattr(args, 'evaporation_coeff') and args.evaporation_coeff is not None:
                params['Evaporation_Coefficient'] = args.evaporation_coeff
                
        elif args.variant == 'kumar':
            if hasattr(args, 'volumetric_heating') and args.volumetric_heating is not None:
                params['Volumetric_Heat_Generation'] = args.volumetric_heating
            if hasattr(args, 'reynolds_number') and args.reynolds_number is not None:
                params['Reynolds_Number'] = args.reynolds_number
            if hasattr(args, 'weber_number') and args.weber_number is not None:
                params['Weber_Number'] = args.weber_number
            if hasattr(args, 'enable_marangoni') and args.enable_marangoni:
                params['Marangoni_Effect'] = True
            if hasattr(args, 'disable_marangoni') and args.disable_marangoni:
                params['Marangoni_Effect'] = False
        
        return params
    
    def _validate_config(self, config_path: str) -> int:
        """Validate configuration file"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.error(f"Config file not found: {config_path}")
                return 1
            
            params = load_config(config_file)
            logger.info(f"✓ Configuration valid: {len(params)} parameters loaded")
            
            # Basic validation
            required_keys = ['Domain_Width', 'Domain_Height', 'Droplet_Radius']
            missing = [key for key in required_keys if key not in params]
            
            if missing:
                logger.warning(f"Missing recommended parameters: {missing}")
                return 1
            
            logger.info("✓ All required parameters present")
            return 0
            
        except Exception as e:
            logger.error(f"Config validation failed: {e}")
            return 1
    
    def _list_defaults(self, variant: str) -> int:
        """List default parameters for variant"""
        try:
            if variant == 'fresnel':
                builder = FresnelModelBuilder({})
            elif variant == 'kumar':
                builder = KumarModelBuilder({})
            else:
                logger.error(f"Unknown variant: {variant}")
                return 1
            
            print(f"\n{variant.title()} Variant Default Parameters:")
            print("=" * 50)
            
            for key, value in sorted(builder.params.items()):
                print(f"{key:<30} = {value}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to list defaults: {e}")
            return 1
    
    def _list_parameters(self, params: Dict[str, Any], variant: str) -> int:
        """List all parameters"""
        print(f"\n{variant.title()} Model Parameters:")
        print("=" * 50)
        
        for key, value in sorted(params.items()):
            print(f"{key:<30} = {value}")
        
        print(f"\nTotal: {len(params)} parameters")
        return 0
    
    def _dry_run(self, params: Dict[str, Any], args: argparse.Namespace) -> int:
        """Perform dry run"""
        print(f"\nDry Run - {args.variant.title()} Model")
        print("=" * 40)
        print(f"Config parameters: {len(params)}")
        print(f"Output directory: {args.output_dir}")
        
        if hasattr(args, 'output') and args.output:
            print(f"Output file: {args.output}")
        
        if args.solve:
            print("Would solve model after building")
        if args.extract_results:
            print("Would extract results after solving")
        
        print("\nNo actual model building performed.")
        return 0
    
    def _validate_only(self, params: Dict[str, Any], variant: str) -> int:
        """Validate parameters and geometry only"""
        try:
            logger.info(f"Validating {variant} model parameters")
            
            # Create builder for validation
            if variant == 'fresnel':
                builder = FresnelModelBuilder(params)
            elif variant == 'kumar':
                builder = KumarModelBuilder(params)
            else:
                raise ValueError(f"Unknown variant: {variant}")
            
            # Validate geometry (without COMSOL)
            from .mph_core.geometry import GeometryBuilder
            mock_model = None  # Geometry validation doesn't need real model
            geom_builder = GeometryBuilder(mock_model, builder.params)
            
            if not geom_builder.validate_geometry():
                logger.error("Geometry validation failed")
                return 1
            
            logger.info("✓ Parameter and geometry validation successful")
            return 0
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 1
    
    def _build_model(self, params: Dict[str, Any], args: argparse.Namespace) -> int:
        """Build model and optionally solve"""
        try:
            logger.info(f"Building {args.variant} model with MPh API")
            
            # Create appropriate builder
            if args.variant == 'fresnel':
                builder_class = FresnelModelBuilder
            elif args.variant == 'kumar':
                builder_class = KumarModelBuilder
            else:
                raise ValueError(f"Unknown variant: {args.variant}")
            
            # Determine output path
            output_path = None
            if hasattr(args, 'output') and args.output:
                output_path = Path(args.output)
            
            # Build model
            with builder_class(params) as builder:
                model_file = builder.build_complete_model(output_path)
                logger.info(f"✓ Model built successfully: {model_file}")
                
                if not args.build_only and (args.solve or args.extract_results):
                    # Solve model
                    logger.info("Solving model...")
                    results = builder.solve_and_extract_results()
                    logger.info(f"✓ Model solved and {len(results)} result files extracted")
                    
                    # Print result files
                    print("\nGenerated Files:")
                    print(f"Model file: {model_file}")
                    for result_type, result_file in results.items():
                        print(f"{result_type}: {result_file}")
                
            return 0
            
        except Exception as e:
            logger.error(f"Model building failed: {e}")
            return 2


def main() -> int:
    """Main entry point for MPh CLI"""
    cli = MPhCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
