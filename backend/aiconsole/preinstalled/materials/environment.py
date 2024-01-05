import getpass
import os
import platform
from datetime import datetime

from aiconsole_toolkit.env import get_current_project_venv_available_packages


async def content(context):
    return f"""
## Execution environment

os: {platform.system()}
cwd: {os.getcwd()}
username: {getpass.getuser()}
time_stamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
python_version: {platform.python_version()}
default_shell: {os.environ.get('SHELL')}

## Python Packages
{get_current_project_venv_available_packages()}
"""
