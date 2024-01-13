import logging
import shutil
import subprocess
import sys

from aiconsole.core.code_running.virtual_env.install_and_upgrade_pip import (
    install_and_update_pip,
)
from aiconsole_toolkit.env import (
    get_current_project_venv_path,
    get_current_project_venv_python_path,
)

_log = logging.getLogger(__name__)


def run_subprocess(*args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        _log.error(f"Command {' '.join(args)} failed with error: {stderr.decode().strip()}")
        raise RuntimeError(stderr.decode().strip())

    return stdout.decode().strip()


def get_python_version(python_executable):
    """Returns the Python version for the given executable."""
    try:
        return run_subprocess(python_executable, "-c", "import sys; print(sys.version)")
    except Exception as e:
        _log.exception(f"Error: {e}")
        return None


async def create_dedicated_venv():
    venv_path = get_current_project_venv_path()
    system_python_version = get_python_version(sys.executable)

    if not venv_path.exists():
        _log.info(f"Creating venv in {venv_path}, using {sys.executable}")
        run_subprocess(sys.executable, "-m", "venv", str(venv_path), "--system-site-packages")
    else:
        _log.info(f"Venv already exists in {venv_path}")

        venv_python_executable = str(get_current_project_venv_python_path())

        venv_python_version = get_python_version(venv_python_executable)
        if venv_python_version:
            _log.info(f"Valid venv python executable")
        else:
            _log.info(f"Reconstructing venv due to the different Python version({system_python_version}):")
            shutil.rmtree(str(get_current_project_venv_path()))
            _log.info(f"1) Deleted old env.")

            run_subprocess(sys.executable, "-m", "venv", str(venv_path), "--system-site-packages")
            _log.info(f"2) Created venv in {venv_path}, using {sys.executable}")

    install_and_update_pip(venv_path)
