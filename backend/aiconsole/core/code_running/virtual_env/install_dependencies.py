import logging
import platform
import subprocess

from aiconsole.consts import DIR_WITH_AICONSOLE_PACKAGE

_log = logging.getLogger(__name__)


def install_dependencies(venv_or_python_path):
    pyproject_path = DIR_WITH_AICONSOLE_PACKAGE / "pyproject.toml"

    if not pyproject_path.exists():
        _log.info(f"Skipping installation: '{pyproject_path}' does not exist (bundled version?)")
        return

    if platform.system() == "Windows":
        python_path = venv_or_python_path / "python.exe"
        install_command = [python_path, "-m", "pip", "install", "-e", str(DIR_WITH_AICONSOLE_PACKAGE)]
    else:
        pip_path = venv_or_python_path / "bin" / "pip"
        install_command = [pip_path, "install", "-e", str(DIR_WITH_AICONSOLE_PACKAGE)]

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
