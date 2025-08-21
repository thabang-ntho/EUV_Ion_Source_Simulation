"""
Kumar 2D Demo — Direct MPh Translation (container API), aligned with mph_example.py

This script translates the COMSOL-exported Java model to MPh Python code using
the container pattern (model/'container') and features known from mph_example.py.

It reads parameters from KUMAR-2D/parameters.txt, builds geometry, functions,
variables, physics (Heat Transfer + Single Phase Flow), mesh, and a transient
study, then saves an .mph file under KUMAR-2D/results/.

Run:
  python KUMAR-2D/kumar_2d_mph.py --check-only   # build only, save mph
  python KUMAR-2D/kumar_2d_mph.py --solve        # build + solve (requires COMSOL)
  python KUMAR-2D/kumar_2d_mph.py --dry-run      # no COMSOL, print plan
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import os


def parse_param_file(p: Path) -> dict[str, str]:
    params: dict[str, str] = {}
    for line in p.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith('%') or s.startswith('#'):
            continue
        parts = s.split()
        if len(parts) < 2:
            continue
        key = parts[0]
        val = ' '.join(parts[1:])
        # Strip inline triple-quote comments and # comments
        if '"""' in val:
            val = val.split('"""', 1)[0].strip()
        if '#' in val:
            val = val.split('#', 1)[0].strip()
        params[key] = val
    return params


def build_model(params: dict, out_path: Path, solve: bool = False) -> None:
    import mph  # imported here to allow --dry-run without mph

    client = None
    host = os.environ.get('COMSOL_HOST')
    port = os.environ.get('COMSOL_PORT')
    cores = os.environ.get('COMSOL_CORES')
    if host and port:
        client = mph.start(host=host, port=int(port))
    elif cores:
        try:
            client = mph.start(cores=int(cores))
        except TypeError:
            client = mph.start()
    else:
        client = mph.start()

    try:
        model = client.create('Kumar_2D')

        # Parameters (assign strings with units/expressions)
        for k, v in params.items():
            model.parameter(k, v)

        # Containers
        functions = model/'functions'
        components = model/'components'
        components.create(True, name='comp1')
        geometries = model/'geometries'
        geometry = geometries.create(2, name='geom1')
        meshes = model/'meshes'
        materials = model/'materials'
        physics = model/'physics'
        studies = model/'studies'
        solutions = model/'solutions'

        # Functions: pulse step, gaussian space factor, surface tension sigma(T)
        step = functions.create('Step', name='pulse')
        step.property('funcname', 'pulse')
        step.property('location', params.get('t_start', '0[s]'))
        # emulate to = t_start + t_pulse by using width via second step or smooth; using smooth only
        step.property('smooth', params.get('eps_t', '1e-9[s]'))

        gauss = functions.create('Analytic', name='gaussXY')
        gauss.property('funcname', 'gaussXY')
        gauss.property('expr', 'exp(-((x-x0)^2 + (y-y0)^2)/(2*G_sigma^2))')
        gauss.property('args', ['x', 'y'])
        gauss.property('argunit', ['m', 'm'])

        sigma_fn = functions.create('Analytic', name='sigma')
        sigma_fn.property('funcname', 'sigma')
        sigma_fn.property('expr', 'sigma_f + d_sigma_dT*(T - Tmelt_sn)')
        sigma_fn.property('args', ['T'])

        # Geometry: rectangle (vacuum box) and circle (droplet)
        rect = geometry.create('Rectangle', name='vac_box')
        rect.property('size', [params.get('W_dom', '200[um]'), params.get('H_dom', '300[um]')])
        circ = geometry.create('Circle', name='droplet')
        circ.property('pos', [params.get('x0', 'W_dom/2'), params.get('y0', 'H_dom/2')])
        circ.property('r', params.get('R_drop', '15[um]'))
        model.build(geometry)

        # Selections (simple): domains and exterior boundary
        selections = model/'selections'
        s_drop = selections.create('Disk', name='s_drop')
        s_drop.property('posx', params.get('x0', 'W_dom/2'))
        s_drop.property('posy', params.get('y0', 'H_dom/2'))
        s_drop.property('r', params.get('R_drop', '15[um]'))

        s_gas = selections.create('Explicit', name='s_gas')
        s_gas.select('all')

        s_surf = selections.create('Adjacent', name='s_surf')
        s_surf.property('input', [s_drop])

        # Materials: tin (droplet) and default gas if needed
        tin = materials.create('Common', name='tin')
        basic = tin/'Basic'
        # Use constant values from parameters
        if 'rho_sn' in params:
            basic.property('density', params['rho_sn'])
        if 'k_sn' in params:
            basic.property('thermalconductivity', params['k_sn'])
        if 'Cp_sn' in params:
            basic.property('heatcapacity', params['Cp_sn'])
        tin.select(s_drop)

        # Physics: Heat Transfer (HT) and Single Phase Flow (SPF)
        ht = physics.create('HeatTransfer', geometry, name='ht')
        ht.select(s_gas)  # include entire domain; tin material applied in region
        # Add volumetric heat source feature using q_laser expr
        htqs = ht.create('HeatSource', 2, name='laser_heating')
        q_expr = '(2*a_abs*P_laser)/(pi*Rl_spot^2)*exp(-2*((x - x0)^2 + (y - y0)^2)/Rl_spot^2)*pulse(t)/1[s]'
        htqs.property('Q0', q_expr)

        spf = physics.create('SinglePhaseFlow', geometry, name='spf')
        spf.select(s_drop)
        # Default no-slip walls implicit; surface tension and Marangoni would be added via dedicated features if needed

        # Mesh
        mesh = meshes.create(geometry, name='mesh1')
        size = mesh.create('Size', name='size')
        size.property('hauto', 3)
        model.build(mesh)

        # Study: Transient
        study = studies.create(name='transient')
        study.java.setGenPlots(False)
        study.java.setGenConv(False)
        step = study.create('Transient', name='time_dependent')
        t_step = params.get('t_step', '5[ns]')
        t_pulse = params.get('t_pulse', '300[ns]')
        step.property('tlist', f'range(0, {t_step}, {t_pulse})')
        step.property('activate', [
            physics/'ht', 'on',
            physics/'spf', 'on',
            'frame:spatial1', 'on',
            'frame:material1', 'on',
        ])

        # Solution
        solution = solutions.create(name='solution')
        solution.java.study(study.tag())
        solution.java.attach(study.tag())
        solution.create('StudyStep', name='equations')
        variables = solution.create('Variables', name='variables')
        variables.property('clist', [f'range(0, {t_step}, {t_pulse})', '0.001[s]'])
        solver = solution.create('Time', name='time_solver')
        solver.property('tlist', f'range(0, {t_step}, {t_pulse})')

        # Save
        model.save(str(out_path))

        if solve:
            study.solve()
            # Export a simple temperature plot
            plots = model/'results'
            pg = plots.create('PlotGroup2D', name='temperature')
            surf = pg.create('Surface', name='T_surface')
            surf.property('expr', 'T')
            out_png = out_path.with_name('temperature_field.png')
            pg.export(str(out_png))
            # Save solved snapshot
            solved = out_path.with_name(out_path.stem + '_solved.mph')
            try:
                model.save(str(solved))
            except Exception:
                pass
    finally:
        try:
            if client:
                client.disconnect()
        except Exception:
            pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description='Kumar 2D MPh translation runner')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--check-only', action='store_true')
    g.add_argument('--solve', action='store_true')
    ap.add_argument('--out', type=str, default=str(Path(__file__).resolve().parent / 'results' / 'kumar2d_model.mph'))
    ap.add_argument('--log-level', type=str, default='INFO')
    args = ap.parse_args(argv)

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    base = Path(__file__).resolve().parent
    params_file = base / 'parameters.txt'
    if not params_file.exists():
        logging.error(f'Missing parameters.txt at {params_file}')
        return 2
    params = parse_param_file(params_file)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        logging.info('Dry-run: would build Kumar 2D using MPh')
        logging.info(f'Output: {out_path}')
        return 0

    build_model(params, out_path, solve=args.solve and not args.check_only)
    logging.info('Done')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
