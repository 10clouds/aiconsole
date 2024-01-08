import logging
import subprocess
from pathlib import Path

from aiconsole.consts import DIR_WITH_AICONSOLE_PACKAGE
from aiconsole_toolkit.env import get_current_project_user_packages

_log = logging.getLogger(__name__)


def install_dependencies(python_path: Path, dependency_file: Path):
    if not dependency_file.exists():
        _log.info(f"Skipping installation: '{dependency_file}' does not exist (bundled version?)")
        return
    if dependency_file == get_current_project_user_packages():
        install_command = [
            str(python_path),
            "-m",
            "pip",
            "install",
            "-r",
            str(dependency_file),
        ]
    else:
        install_command = [
            str(python_path),
            "-m",
            "pip",
            "install",
            "-e",
            str(DIR_WITH_AICONSOLE_PACKAGE),
        ]

    _log.info(f"Installing aiconsole and dependencies using: {' '.join([str(elem) for elem in install_command])}")

    try:
        result = subprocess.run(
            [str(elem) for elem in install_command],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _log.info(f"Installation successful: {result.stdout}")
    except subprocess.CalledProcessError as e:
        _log.error(f"Installation failed: {e.stderr}")
