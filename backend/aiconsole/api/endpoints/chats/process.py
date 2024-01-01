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

import asyncio
import importlib
import logging
from uuid import uuid4

from aiconsole.api.websockets.outgoing_messages import ErrorWSMessage, RequestProcessingFinishedWSMessage
from aiconsole.core.analysis.director import director_analyse
from aiconsole.core.assets.agents.agent import Agent, ExecutionModeContext
from aiconsole.core.assets.materials.content_evaluation_context import ContentEvaluationContext
from aiconsole.core.chat.chat_mutator import ChatMutator
from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.types import AICMessageGroup
from aiconsole.core.chat.ws_chat_listener import WSChatListener
from aiconsole.utils.cancel_on_disconnect import cancelable_endpoint
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()
_log = logging.getLogger(__name__)


class ProcessRequestData(BaseModel):
    request_id: str


async def dynamic_import_and_call_execution_mode(agent: Agent, context):
    execution_mode = agent.execution_mode

    split = execution_mode.split(":")

    if len(split) != 2:
        raise ValueError(
            f"Invalid execution_mode in agent {agent.name}: {execution_mode} - should be module_name:object_name"
        )

    module_name, object_name = execution_mode.split(":")
    module = importlib.import_module(module_name)
    obj = getattr(module, object_name, None)

    if obj is None:
        raise ValueError(f"Could not find {object_name} in {module_name} module in agent {agent.name}")

    if not callable(obj):
        raise ValueError(f"{object_name} in {module_name} is not callable (in agent {agent.name})")

    ret_val = obj(context)

    if not asyncio.iscoroutine(ret_val):
        raise ValueError(f"{object_name} in {module_name} is not a coroutine (in agent {agent.name})")

    await ret_val


@router.post("/{chat_id}/process")
@cancelable_endpoint
async def process(request: Request, data: ProcessRequestData, chat_id):
    aborted = False

    # Load and lock chat
    chat = await load_chat_history(chat_id)
    listener = WSChatListener(chat_id=chat_id, request_id=data.request_id)
    chat_mutator = ChatMutator(chat=chat, listener=listener)

    try:
        analysis = await director_analyse(chat_mutator)

        if analysis.agent.id != "user" and analysis.next_step:
            chat.message_groups.append(
                AICMessageGroup(
                    id=str(uuid4()),
                    agent_id=analysis.agent.id,
                    task=analysis.next_step,
                    materials_ids=[material.id for material in analysis.relevant_materials],
                    role="assistant",
                    messages=[],
                    analysis="",
                )
            )

            content_context = ContentEvaluationContext(
                chat=chat,
                agent=analysis.agent,
                gpt_mode=analysis.agent.gpt_mode,
                relevant_materials=analysis.relevant_materials,
            )

            rendered_materials = [
                await material.render(content_context) for material in content_context.relevant_materials
            ]

            context = ExecutionModeContext(
                chat_mutator=chat_mutator,
                agent=analysis.agent,
                rendered_materials=rendered_materials,
                message_group=chat.message_groups[-1],
            )

            await dynamic_import_and_call_execution_mode(analysis.agent, context)
    except asyncio.CancelledError:
        _log.info("Cancelled processingx")
        aborted = True
    except Exception as e:
        _log.exception("Analysis failed", exc_info=e)
        await ErrorWSMessage(error=str(e)).send_to_chat(chat_id)
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await RequestProcessingFinishedWSMessage(request_id=data.request_id, aborted=aborted).send_to_chat(chat_id)
