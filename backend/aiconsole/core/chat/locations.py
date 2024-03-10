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
from fastmutation.data_context import DataContext
from fastmutation.types import (
    AttributeRef,
    CollectionRef,
    ObjectRef,
    StringAttributeRef,
)


class AssetCollectionRef(CollectionRef):
    id: str = "assets"
    parent: None = None


class AssetRef(ObjectRef):
    parent: AssetCollectionRef

    def __init__(self, id: str, context: DataContext):
        super().__init__(id=id, parent_collection=AssetCollectionRef(context=context), context=context)


class ChatRef(ObjectRef[AICChat]):
    parent: AssetCollectionRef

    def __init__(self, id: str, context: DataContext):
        super().__init__(id=id, parent_collection=AssetCollectionRef(context=context), context=context)

    @property
    def message_groups(self):
        return MessageGroupsRef(parent=self, context=self.context)

    @property
    def is_analysis_in_progress(self):
        return AttributeRef[bool](object=self, name="is_analysis_in_progress", context=self.context)

    @property
    def chat_options(self):
        return AttributeRef[AICChatOptions](object=self, name="chat_options", context=self.context)


class MessageGroupsRef(CollectionRef[AICMessageGroup]):
    id: str = "message_groups"
    parent: ChatRef

    def __getitem__(self, id: str) -> "MessageGroupRef":
        return MessageGroupRef(id=id, parent_collection=self, context=self.context)


class MessageGroupRef(ObjectRef[AICMessageGroup]):
    parent_collection: MessageGroupsRef

    @property
    def messages(self):
        return MessagesRef(parent=self, context=self.context)

    @property
    def actor_id(self):
        return AttributeRef[ActorId](object=self, name="actor_id", context=self.context)

    @property
    def materials_ids(self):
        return AttributeRef[list[str]](object=self, name="materials_ids", context=self.context)

    @property
    def task(self):
        return StringAttributeRef(object=self, name="task", context=self.context)

    @property
    def analysis(self):
        return StringAttributeRef(object=self, name="analysis", context=self.context)


class MessagesRef(CollectionRef[AICMessage]):
    id: str = "messages"
    parent: MessageGroupRef

    def __getitem__(self, id: str) -> "MessageRef":
        return MessageRef(id=id, parent_collection=self, context=self.context)


class MessageRef(ObjectRef[AICMessage]):
    parent_collection: MessagesRef

    @property
    def tool_calls(self):
        return ToolCallsRef(parent=self, context=self.context)

    @property
    def content(self):
        return StringAttributeRef(object=self, name="content", context=self.context)

    @property
    def is_streaming(self):
        return AttributeRef[bool](object=self, name="is_streaming", context=self.context)


class ToolCallsRef(CollectionRef[AICToolCall]):
    id: str = "tool_calls"
    parent: MessageRef

    def __getitem__(self, id: str) -> "ToolCallRef":
        return ToolCallRef(parent_collection=self, id=id, context=self.context)

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
    parent_collection: ToolCallsRef

    @property
    def headline(self):
        return StringAttributeRef(object=self, name="headline", context=self.context)

    @property
    def language(self):
        return StringAttributeRef[LanguageStr | None](object=self, name="language", context=self.context)

    @property
    def is_executing(self):
        return AttributeRef[bool](object=self, name="is_executing", context=self.context)

    @property
    def is_successful(self):
        return AttributeRef[bool](object=self, name="is_successful", context=self.context)

    @property
    def is_streaming(self):
        return AttributeRef[bool](object=self, name="is_streaming", context=self.context)

    @property
    def output(self):
        return StringAttributeRef[str | None](object=self, name="output", context=self.context)

    @property
    def code(self):
        return StringAttributeRef(object=self, name="code", context=self.context)

    async def get(self) -> AICToolCall:
        return cast(AICToolCall, await super().get())
