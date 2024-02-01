from typing import Optional

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from aiconsole.core.chat.load_chat_history import load_chat_history
from aiconsole.core.chat.save_chat_history import save_chat_history

router = APIRouter()


class PatchChatOptions(BaseModel):
    agent_id: Optional[str] = None
    materials_ids: Optional[list[str]] = None
    let_ai_add_extra_materials: Optional[bool] = None


@router.patch("/{chat_id}")
async def chat_options(chat_id: str, chat_options: PatchChatOptions):
    chat = await load_chat_history(id=chat_id)
    for field in chat_options.model_dump(exclude_unset=True):
        setattr(chat.chat_options, field, getattr(chat_options, field))
    save_chat_history(chat)
    return Response(status_code=status.HTTP_200_OK)
