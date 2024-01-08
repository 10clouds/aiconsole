from abc import ABC, abstractmethod
from typing import Callable


class SettingsObserver(ABC):
    @abstractmethod
    def start(self, action: Callable):
        ...

    @abstractmethod
    def stop(self):
        ...
