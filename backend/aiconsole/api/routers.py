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

from fastapi import APIRouter

from aiconsole.api.endpoints import (
    assets,
    check_key,
    commands_history,
    genui,
    image,
    net_check,
    ping,
    profile,
    projects,
    settings,
    ws,
)

app_router = APIRouter()

app_router.include_router(ping.router)
app_router.include_router(genui.router)
app_router.include_router(image.router)
app_router.include_router(check_key.router)
app_router.include_router(net_check.router)
app_router.include_router(profile.router, tags=["Profile"])
app_router.include_router(assets.router, prefix="/api/assets", tags=["Agents"])
app_router.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app_router.include_router(settings.router, prefix="/api/settings", tags=["Project Settings"])
app_router.include_router(commands_history.router)
app_router.include_router(ws.router)
