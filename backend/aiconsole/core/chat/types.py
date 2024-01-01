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

from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from aiconsole.core.assets.asset import EditableObject

from aiconsole.core.code_running.code_interpreters.language_map import LanguageStr
from aiconsole.core.gpt.types import GPTRole
from aiconsole.core.settings.project_settings import get_aiconsole_settings
from pydantic import BaseModel, Field, model_validator


class AICToolCall(BaseModel):
    id: str
    language: LanguageStr | None = None
    code: str
    headline: str
    output: str | None = None

    is_streaming: bool = False
    is_executing: bool = False


class AICMessage(BaseModel):
    id: str
    timestamp: str
    content: str
    tool_calls: list[AICToolCall]

    is_streaming: bool = False


class AICMessageGroup(BaseModel):
    id: str
    agent_id: str
    username: str | None = None
    email: str | None = None
    role: GPTRole
    analysis: str
    task: str
    agent_id: str
    materials_ids: list[str]
    role: GPTRole
    messages: list[AICMessage]

    @model_validator(mode="after")
    def set_default_username(self):
        role = self.role
        if role == "user":
            self.username = self.username or get_aiconsole_settings().get_username()
        return self

    @model_validator(mode="after")
    def set_default_email(self):
        role = self.role
        if role == "user":
            self.email = self.email or get_aiconsole_settings().get_email()
        return self


class ChatHeadline(EditableObject):
    last_modified: datetime

    def model_dump(self, **kwargs):
        return {
            **super().model_dump(**kwargs),
            "last_modified": self.last_modified.isoformat(),
        }


@dataclass
class AICMessageInfo:
    message_group: AICMessageGroup
    message: AICMessage


@dataclass
class AICToolCallInfo:
    message_group: AICMessageGroup
    message: AICMessage
    tool_call: AICToolCall


class Chat(ChatHeadline):
    title_edited: bool = False
    message_groups: list[AICMessageGroup]
    is_analysis_in_progress: bool = False

    def get_message_group(self, message_group_id: str) -> AICMessageGroup | None:
        for message_group in self.message_groups:
            if message_group.id == message_group_id:
                return message_group
        return None

    def get_message(self, message_id: str) -> AICMessageInfo | None:
        for message_group in self.message_groups:
            for message in message_group.messages:
                if message.id == message_id:
                    return AICMessageInfo(message_group=message_group, message=message)
        return None

    def get_tool_call(self, tool_call_id: str) -> AICToolCallInfo | None:
        for message_group in self.message_groups:
            for message in message_group.messages:
                for tool_call in message.tool_calls:
                    if tool_call.id == tool_call_id:
                        return AICToolCallInfo(message_group=message_group, message=message, tool_call=tool_call)
        return None


class Command(BaseModel):
    command: str


class ChatHeadlines(BaseModel):
    headlines: list[ChatHeadline]
