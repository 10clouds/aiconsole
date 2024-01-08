from functools import lru_cache

from aiconsole.api.endpoints.projects.services import ProjectDirectory


@lru_cache()
def project_directory() -> ProjectDirectory:
    return ProjectDirectory()
