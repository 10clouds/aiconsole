import logging
import subprocess
import sys

from aiconsole.core.code_running.virtual_env.install_and_upgrade_pip import (
    install_and_update_pip,
)
from aiconsole.core.code_running.virtual_env.install_dependencies import (
    install_dependencies,
)
from aiconsole_toolkit.env import get_current_project_venv_path

_log = logging.getLogger(__name__)


async def create_dedicated_venv():
    venv_path = get_current_project_venv_path()  # Ensure this function returns a Path object
    if not venv_path.exists():
        _log.info(f"Creating venv in {venv_path}")
        subprocess.Popen(
            [sys.executable, "-m", "venv", venv_path, "--system-site-packages"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
    else:
        _log.info(f"Venv already exists in {venv_path}")

    install_and_update_pip(venv_path)
    install_dependencies(venv_path)
