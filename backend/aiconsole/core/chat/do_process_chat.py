import logging
import random
from typing import cast
from uuid import uuid4

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.render_materials import render_materials
from aiconsole.api.websockets.server_messages import (
    ErrorServerMessage,
    NotificationServerMessage,
)
from aiconsole.consts import DIRECTOR_AGENT_ID
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.types import AssetType
from aiconsole.core.chat.actor_id import ActorId
from aiconsole.core.chat.execution_modes.analysis.agents_to_choose_from import (
    agents_to_choose_from,
)
from aiconsole.core.chat.execution_modes.utils.import_and_validate_execution_mode import (
    import_and_validate_execution_mode,
)
from aiconsole.core.chat.locations import ChatRef
from aiconsole.core.chat.types import AICMessageGroup
from aiconsole.core.gpt.types import GPTRole
from aiconsole.core.project import project

_log = logging.getLogger(__name__)


async def do_process_chat(chat_ref: ChatRef):
    role: GPTRole = "assistant"

    agent: AICAgent | None = None
    visible_agent_id = None

    if (await chat_ref.chat_options.get()).agent_id:
        # The user selected an agent for the chat
        for _agent in agents_to_choose_from():
            if _agent.id == (await chat_ref.chat_options.get()).agent_id:
                agent = _agent

        if not agent:
            await connection_manager().send_to_all(
                ErrorServerMessage(
                    error="The selected agent does not exist or is disabled, please select a different agent.",
                )
            )
            return

    if not agent or (await chat_ref.chat_options.get()).ai_can_add_extra_materials:
        # We need to run the director agent

        director_agent = cast(
            AICAgent | None,
            project.get_project_assets().get_asset(DIRECTOR_AGENT_ID, type=AssetType.AGENT, enabled=True),
        )

        if director_agent:
            role = "system"  # TODO: This should be read from the agent, not hardcoded

            if agent:
                # We want to show the chosen agent as the visible agent, even though the director agent is doing the analysis first
                visible_agent_id = agent.id

            agent = director_agent
        else:
            message: str = ""

            if agent:
                message = "Can not add extra materials."
            else:
                possible_agents = agents_to_choose_from()

                # assign a random agent to the chat
                if possible_agents:
                    message = "No director agent found, using a random agent for the chat with no extra materials."
                    agent = random.choice(possible_agents)

            if message:
                await connection_manager().send_to_all(
                    NotificationServerMessage(
                        title="No director agent found",
                        message=message,
                    )
                )

    if not agent:
        await connection_manager().send_to_all(
            ErrorServerMessage(
                error="No agents found, please create an agent before processing the chat.",
            )
        )
        return

    materials_ids = (await chat_ref.chat_options.get()).materials_ids or []

    if materials_ids:
        try:
            materials_and_rmats = await render_materials(materials_ids, await chat_ref.get(), agent, init=True)
        except ValueError:
            _log.debug(f"Failed to render materials {materials_ids} for chat {chat_ref.id}")
            return

        materials = materials_and_rmats.materials
        rendered_materials = materials_and_rmats.rendered_materials
    else:
        materials = []
        rendered_materials = []

    # Create a new message group for analysis
    message_group_id = str(uuid4())

    await chat_ref.message_groups.create(
        AICMessageGroup(
            id=message_group_id,
            actor_id=ActorId(type="agent", id=visible_agent_id or agent.id),
            role=role,
            materials_ids=materials_ids,
            analysis="",
            task="",
            messages=[],
        ),
    )

    execution_mode = await import_and_validate_execution_mode(agent, chat_ref)

    await execution_mode.process_chat(
        chat_ref=chat_ref,
        agent=agent,
        materials=materials,
        rendered_materials=rendered_materials,
    )
