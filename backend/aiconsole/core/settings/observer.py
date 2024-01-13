import logging
from functools import lru_cache
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer

from aiconsole.utils.BatchingWatchDogHandler import BatchingWatchDogHandler

_log = logging.getLogger(__name__)


class FileObserver:
    def __init__(self):
        self._observer = None
        self.observing: list[Path] = []

    def start(self, file_paths: list[Path], action: Callable):
        _log.debug(f"[{self.__class__.__name__}] Starting observer...")

        # Stop and reset the existing observer
        self.stop()

        # Reinitialize the observer
        self._observer = Observer()

        # Setup and start new observer
        for file_path in file_paths:
            if not isinstance(file_path, Path):
                _log.error(f"[{self.__class__.__name__}] Not a valid filepath: {file_path}")
                continue

            if file_path in self.observing:
                _log.warning(f"[{self.__class__.__name__}] Already observing: {file_path}")
                continue

            # Set up observer
            try:
                self._observer.schedule(
                    BatchingWatchDogHandler(action, file_path.suffix),
                    file_path.parent,
                    recursive=False,
                )
            except Exception as e:
                _log.error(f"[{self.__class__.__name__}] Error setting up observer for {file_path}: {e}")

            self.observing.append(file_path)

        if self.observing:
            try:
                self._observer.start()
                _log.info(f"[{self.__class__.__name__}] Observing for changes: {', '.join(map(str, self.observing))}.")
            except RuntimeError as e:
                _log.error(f"[{self.__class__.__name__}] Error starting observer: {e}")

    def stop(self):
        if self._observer and self._observer.is_alive():
            try:
                self._observer.stop()
                self._observer.join()
            except Exception as e:
                _log.error(f"[{self.__class__.__name__}] Error stopping observer: {e}")
            finally:
                self.observing.clear()
                _log.info(f"[{self.__class__.__name__}] Observer stopped.")
        else:
            _log.info(f"[{self.__class__.__name__}] Observer was not running or not initialized.")


@lru_cache
def file_observer() -> FileObserver:
    return FileObserver()
