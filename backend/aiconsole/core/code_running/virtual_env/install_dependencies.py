import logging
import subprocess
from pathlib import Path

_log = logging.getLogger(__name__)


def install_dependencies(python_path: Path, dependency_path: Path):
    if not dependency_path.exists():
        _log.info(f"Skipping installation: '{dependency_path}' does not exist (bundled version?)")
        return

    install_command = [python_path, "-m", "pip", "install", dependency_path]
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
