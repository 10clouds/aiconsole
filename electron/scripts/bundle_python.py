# The AIConsole Project
#
# Copyright 2023 10Clouds
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import platform
import sys
from pathlib import Path

python_dir = Path(".") / "python"

# Add aiconsole dir to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

import logging

from aiconsole.consts import DIR_WITH_AICONSOLE_PACKAGE
from aiconsole.core.code_running.virtual_env.download_python import download_python
from aiconsole.core.code_running.virtual_env.install_dependencies import (
    install_dependencies,
)

# setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

_log = logging.getLogger(__name__)

DATE_TAG = "20231002"
PYTHON_VERSION = f"3.11.6+{DATE_TAG}"


def check_installation():
    if python_dir.is_dir():
        _log.info("Python already installed.")
    else:
        if not download_python(PYTHON_VERSION, DATE_TAG):
            _log.error("Python download and extraction failed.")
            exit(1)

    if platform.system() == "Windows":
        python_path = python_dir / "python.exe"
    else:
        python_path = python_dir / "bin" / "python3"
    install_dependencies(python_path=python_path, dependency_path=DIR_WITH_AICONSOLE_PACKAGE)
    _log.info("Build process completed!")


def main():
    check_installation()


if __name__ == "__main__":
    main()
