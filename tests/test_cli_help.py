import subprocess, sys


def test_mph_runner_help():
    res = subprocess.run([sys.executable, '-m', 'src.cli.mph_runner', '--help'], capture_output=True, text=True)
    assert res.returncode == 0
    assert 'Build and optionally solve' in res.stdout
    assert '--check-only' in res.stdout
    assert '--solve' in res.stdout

