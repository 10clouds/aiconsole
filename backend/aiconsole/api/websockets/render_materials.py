from dataclasses import dataclass
from typing import cast

from aiconsole.api.websockets.connection_manager import connection_manager
from aiconsole.api.websockets.server_messages import ErrorServerMessage
from aiconsole.core.assets.agents.agent import AICAgent
from aiconsole.core.assets.materials.content_evaluation_context import (
    ContentEvaluationContext,
)
from aiconsole.core.assets.materials.material import (
    AICMaterial,
    MaterialRenderErrorEvent,
)
from aiconsole.core.assets.materials.rendered_material import RenderedMaterial
from aiconsole.core.chat.locations import AssetRef
from aiconsole.core.chat.types import AICChat
from aiconsole.core.project import project
from aiconsole.utils.events import InternalEvent, internal_events


@dataclass
class MaterialsAndRenderedMaterials:
    materials: list[AICMaterial]
    rendered_materials: list[RenderedMaterial]


async def render_materials(
    materials_ids: list[str], chat: AICChat, agent: AICAgent, init: bool = False
) -> MaterialsAndRenderedMaterials:
    events_to_sub: list[type[InternalEvent]] = [
        MaterialRenderErrorEvent,
    ]

    async def _notify(event, **kwargs):
        if isinstance(event, MaterialRenderErrorEvent):
            await connection_manager().send_to_ref(
                ErrorServerMessage(error=f"Incorrect material. {kwargs.get('details')}"),
                AssetRef(id=chat.id, context=None),
            )

    try:
        for event in events_to_sub:
            internal_events().subscribe(
                event,
                _notify,
            )

        relevant_materials = [
            cast(AICMaterial, project.get_project_assets().get_asset(material_id)) for material_id in materials_ids
        ]

        content_context = ContentEvaluationContext(
            chat=chat,
            agent=agent,
            gpt_mode=agent.gpt_mode,
            relevant_materials=relevant_materials,
        )

        rendered_materials = []
        for material in relevant_materials:
            rendered_material = await material.render(content_context)
            rendered_materials.append(rendered_material)

        return MaterialsAndRenderedMaterials(materials=relevant_materials, rendered_materials=rendered_materials)
    finally:
        for event in events_to_sub:
            internal_events().unsubscribe(
                event,
                _notify,
            )
