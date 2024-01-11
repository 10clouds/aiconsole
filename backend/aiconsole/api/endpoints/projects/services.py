import os
from pathlib import Path
from tkinter import Tk, filedialog

from fastapi import BackgroundTasks

from aiconsole.core.project.paths import get_project_directory
from aiconsole.core.project.project import choose_project, is_project_initialized


class ProjectDirectory:
    def __init__(self) -> None:
        self._root = None

    async def choose_directory(self) -> Path | None:
        if not self._root:
            self._root = Tk()
        else:
            self._root.deiconify()
        self._root.withdraw()
        initial_dir = get_project_directory() if is_project_initialized() else os.getcwd()
        directory = filedialog.askdirectory(initialdir=initial_dir)

        # Check if the dialog was cancelled (directory is an empty string)
        if directory == "":
            return None
        else:
            return Path(directory)

    def is_project_in_directory(self, directory: str) -> bool:
        directory = Path(directory)
        return directory.joinpath("materials").is_dir() or directory.joinpath("agents").is_dir()

    async def switch_or_save_project(self, directory: str, background_tasks: BackgroundTasks) -> bool:
        await choose_project(path=Path(directory), background_tasks=background_tasks)
