from typing import cast

from aiconsole.core.chat.actor_id import ActorId
from aiconsole.core.chat.types import (
    AICChat,
    AICChatOptions,
    AICMessage,
    AICMessageGroup,
    AICToolCall,
)
from aiconsole.core.code_running.code_interpreters.language import LanguageStr
from fastmutation.types import (
    AttributeRef,
    CollectionRef,
    MutationExecutor,
    ObjectRef,
    StringAttributeRef,
)


class AssetsRef(CollectionRef):
    id: str = "assets"
    parent: None = None


class AssetRef(ObjectRef):
    parent: AssetsRef = AssetsRef()


class ChatRef(ObjectRef[AICChat]):
    parent: AssetsRef = AssetsRef()

    @property
    def message_groups(self):
        return MessageGroupsRef(parent=self)

    @property
    def is_analysis_in_progress(self):
        return AttributeRef[bool](object=self, name="is_analysis_in_progress")

    @property
    def chat_options(self):
        return AttributeRef[AICChatOptions](object=self, name="chat_options")


class MessageGroupsRef(CollectionRef[AICMessageGroup]):
    id: str = "message_groups"
    parent: ChatRef

    def __getitem__(self, id: str) -> "MessageGroupRef":
        return MessageGroupRef(id=id, parent=self)


class MessageGroupRef(ObjectRef[AICMessageGroup]):
    parent: MessageGroupsRef

    @property
    def messages(self):
        return MessagesRef(parent=self)

    @property
    def actor_id(self):
        return AttributeRef[ActorId](object=self, name="actor_id")

    @property
    def materials_ids(self):
        return AttributeRef[list[str]](object=self, name="materials_ids")

    @property
    def task(self):
        return StringAttributeRef(object=self, name="task")

    @property
    def analysis(self):
        return StringAttributeRef(object=self, name="analysis")


class MessagesRef(CollectionRef[AICMessage]):
    id: str = "messages"
    parent: MessageGroupRef

    def __getitem__(self, id: str) -> "MessageRef":
        return MessageRef(id=id, parent=self)


class MessageRef(ObjectRef[AICMessage]):
    parent: MessagesRef

    @property
    def tool_calls(self):
        return ToolCallsRef(parent=self)

    @property
    def content(self):
        return StringAttributeRef(object=self, name="content")

    @property
    def is_streaming(self):
        return AttributeRef[bool](object=self, name="is_streaming")


class ToolCallsRef(CollectionRef[AICToolCall]):
    id: str = "tool_calls"
    parent: MessageRef

    def __getitem__(self, id: str) -> "ToolCallRef":
        return ToolCallRef(parent=self, id=id)

    # HANDLE DELETE

    # Remove message group if it's empty
    # if not message_location.message_group.messages:
    #     chat.message_groups = [group for group in chat.message_groups if group.id != message_location.message_group.id]

    # Remove message group if it's empty
    # if not tool_call.message_group.messages:
    #    chat.message_groups = [group for group in chat.message_groups if group.id != tool_call.message_group.id]

    # SET VSALUE

    # _handle_SetMessageGroupAgentIdMutation
    # if mutation.actor_id == "user":
    #     message_group.role = "user"
    # else:
    #    message_group.role = "assistant"
    #    message_group.agent_id = mutation.actor_id


class ToolCallRef(ObjectRef):
    parent: ToolCallsRef

    @property
    def headline(self):
        return StringAttributeRef(object=self, name="headline")

    @property
    def language(self):
        return StringAttributeRef[LanguageStr | None](object=self, name="language")

    @property
    def is_executing(self):
        return AttributeRef[bool](object=self, name="is_executing")

    @property
    def is_successful(self):
        return AttributeRef[bool](object=self, name="is_successful")

    @property
    def is_streaming(self):
        return AttributeRef[bool](object=self, name="is_streaming")

    @property
    def output(self):
        return StringAttributeRef[str | None](object=self, name="output")

    @property
    def code(self):
        return StringAttributeRef(object=self, name="code")

    def get(self, executor: MutationExecutor) -> AICToolCall:
        return cast(AICToolCall, executor.get(self))
