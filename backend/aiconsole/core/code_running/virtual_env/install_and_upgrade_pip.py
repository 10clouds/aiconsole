import logging
import platform
import shlex
import subprocess
from pathlib import Path

_log = logging.getLogger(__name__)


def install_and_update_pip(venv_path):
    venv_path = Path(venv_path)

    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        pip_path = venv_path / "bin" / "pip"

    def run_subprocess(*args):
        process = subprocess.Popen(
            [str(pip_path), "install", "--upgrade", "pip"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            _log.error(f"Command {' '.join(args)} failed with error: {stderr.decode().strip()}")
            raise RuntimeError(stderr.decode().strip())

        return stdout.decode().strip()

    if not pip_path.exists():
        _log.info("Installing pip in the virtual environment.")
        run_subprocess(str(venv_path / "bin" / "python"), "-m", "ensurepip")

    _log.info("Upgrading pip in the virtual environment.")
    run_subprocess(str(pip_path), "install", "--upgrade", "pip")
    return True
