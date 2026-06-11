"""Recovered page module.

The original UTF-8 source was damaged by a Windows encoding rewrite during maintenance.
This loader executes the last valid CPython 3.11 bytecode snapshot kept in
recovery_backup_20260529/pages_pyc so the application remains restartable.
"""
from pathlib import Path
import marshal


def _load_recovered_module() -> None:
    pyc_path = (
        Path(__file__).resolve().parents[2]
        / 'recovery_backup_20260529'
        / 'pages_pyc'
        / f'{Path(__file__).stem}.cpython-311.pyc'
    )
    with pyc_path.open('rb') as pyc_file:
        pyc_file.read(16)
        code = marshal.load(pyc_file)
    exec(code, globals())


_load_recovered_module()
del _load_recovered_module, marshal
