import { AICChatOptions } from '@/types/assets/chatTypes';
import { AttributeRef, CollectionRef, ObjectRef, StringAttributeRef } from './types';
import { AICChat, AICMessage, AICMessageGroup, AICToolCall, Asset } from './constructors';
import { DataContext } from './DataContext';

// COLLECTION REFS
export class AssetsCollectionRef extends CollectionRef<Asset> {
  constructor(context: DataContext | null = null) {
    super('assets', null, context);
  }
}

export class MessagesGroupCollectionRef extends CollectionRef<AICMessageGroup> {
  constructor(id: string, context: DataContext | null = null) {
    super('message_groups', new ChatRef(id, context), context);
  }

  getById(id: string) {
    return new MessageGroupRef(id, this.context);
  }
}

export class MessagesCollectionRef extends CollectionRef<AICMessage> {
  constructor(id: string, context: DataContext | null = null) {
    super('messages', new MessageGroupRef(id, context), context);
  }

  getById(id: string) {
    return new MessageRef(id, this.context);
  }
}

export class ToolCallsCollectionRef extends CollectionRef<AICToolCall> {
  constructor(id: string, context: DataContext | null = null) {
    super('tool_calls', new ToolCallRef(id, context), context);
  }

  getById(id: string) {
    return new ToolCallRef(id, this.context);
  }
}
// OBJECT REFS
export class AssetRef extends ObjectRef<Asset> {
  constructor(id: string, context: DataContext | null = null) {
    super(id, new AssetsCollectionRef(context), context);
  }
}

export class ChatRef extends ObjectRef<AICChat> {
  constructor(id: string, context: DataContext | null = null) {
    super(id, new AssetsCollectionRef(context), context);
  }

  get messagesGroups() {
    return new MessagesGroupCollectionRef(this.id, this.context);
  }

  get isAnalysisInProgress() {
    return new AttributeRef<boolean>('is_analysis_in_progress', this, this.context);
  }

  get chat_options() {
    return new AttributeRef<AICChatOptions>('chat_options', this, this.context);
  }
}

export class MessageGroupRef extends ObjectRef<AICMessageGroup> {
  constructor(id: string, context: DataContext | null = null) {
    super(id, new MessagesGroupCollectionRef(id, context), context);
  }

  get messages() {
    return new MessagesCollectionRef(this.id, this.context);
  }

  get actor_id() {
    return new AttributeRef<string>('actor_id', this, this.context);
  }

  get materials_ids() {
    return new AttributeRef<string[]>('materials_ids', this, this.context);
  }

  get task() {
    return new StringAttributeRef('task', this, this.context);
  }

  get analysis() {
    return new StringAttributeRef('analysis', this, this.context);
  }
}

export class MessageRef extends ObjectRef<AICMessage> {
  constructor(id: string, context: DataContext | null = null) {
    super(id, new MessagesCollectionRef(id, context), context);
  }

  get tool_calls() {
    return new ToolCallsCollectionRef(this.id, this.context);
  }

  get content() {
    return new StringAttributeRef('content', this, this.context);
  }

  get is_streaming() {
    return new AttributeRef<boolean>('is_streaming', this, this.context);
  }
}

export class ToolCallRef extends ObjectRef<AICToolCall> {
  constructor(id: string, context: DataContext | null = null) {
    super(id, new ToolCallsCollectionRef(id, context), context);
  }

  get headline() {
    return new StringAttributeRef('headline', this, this.context);
  }

  get language() {
    return new StringAttributeRef('language', this, this.context);
  }

  get is_executing() {
    return new AttributeRef<boolean>('is_executing', this, this.context);
  }

  get is_successful() {
    return new AttributeRef<boolean>('is_successful', this, this.context);
  }

  get is_streaming() {
    return new AttributeRef<boolean>('is_streaming', this, this.context);
  }

  get output() {
    return new StringAttributeRef('output', this, this.context);
  }

  get code() {
    return new StringAttributeRef('code', this, this.context);
  }
}
