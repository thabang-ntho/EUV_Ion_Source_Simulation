from src.core.solvers.sweep import sweep


def test_sweep_stub_runs_worker():
    grid = {"a": [1, 2], "b": ["x"]}
    def worker(cfg):
        return f"{cfg['a']}{cfg['b']}"
    results = sweep(grid, worker)
    pairs = dict((tuple(sorted(cfg.items())), res) for cfg, res in results)
    assert (('a', 1), ('b', 'x')) in pairs
    assert (('a', 2), ('b', 'x')) in pairs
