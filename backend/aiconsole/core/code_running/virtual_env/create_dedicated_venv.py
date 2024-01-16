import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass

import pkg_resources

from aiconsole.consts import DIR_WITH_AICONSOLE_PACKAGE
from aiconsole.core.code_running.virtual_env.install_and_upgrade_pip import (
    install_and_update_pip,
)
from aiconsole.core.code_running.virtual_env.install_dependencies import (
    install_dependencies,
)
from aiconsole.utils.events import InternalEvent
from aiconsole_toolkit.env import (
    get_current_project_venv_path,
    get_current_project_venv_python_path,
)

_log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class WaitForEnvEvent(InternalEvent):
    pass


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


def save_current_app_version_to_venv():
    venv_path = get_current_project_venv_path()
    version_file_path = venv_path / "aic_version"
    with open(version_file_path, "w") as f:
        f.write(venv_version_string())


def venv_version_string():
    version = pkg_resources.get_distribution("aiconsole").version
    version += f" (Python {sys.version.split(' ')[0]})"
    if is_web_server_dev_editable_version():
        version += " (Editable version)"
    return version


def is_web_server_dev_editable_version():
    return (DIR_WITH_AICONSOLE_PACKAGE / "pyproject.toml").exists()


def get_current_app_version_from_venv():
    venv_path = get_current_project_venv_path()
    version_file_path = venv_path / "aic_version"
    if version_file_path.exists():
        with open(version_file_path, "r") as f:
            return f.read()
    return None


def create_dedicated_venv():
    venv_path = get_current_project_venv_path()

    if not venv_path.exists() or get_current_app_version_from_venv() != venv_version_string():
        if venv_path.exists():
            _log.info(
                f"Deleting old ({get_current_app_version_from_venv()}) venv in {venv_path}, new version: {venv_version_string()}"
            )
            shutil.rmtree(venv_path)

        _log.info(f"Creating venv in {venv_path}, using {sys.executable}")

        run_subprocess(sys.executable, "-m", "venv", str(venv_path), "--system-site-packages")

        install_and_update_pip(venv_path)

        if is_web_server_dev_editable_version():
            install_dependencies(get_current_project_venv_python_path(), DIR_WITH_AICONSOLE_PACKAGE)
        else:
            _log.info(
                f"Skipping installation: '{DIR_WITH_AICONSOLE_PACKAGE}' does not contain pyproject.toml (bundled version?)"
            )

        save_current_app_version_to_venv()
    else:
        _log.info(f"Venv already exists in {venv_path}")
