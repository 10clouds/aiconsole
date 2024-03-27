import * as t from '@/types/assets/assetTypes';
import * as ct from '@/types/assets/chatTypes';
import { v4 as uuidv4 } from 'uuid';
import { BaseObject } from './types';

type AICMessageLocation = { group: ct.AICMessageGroup; message: ct.AICMessage } | undefined;
type AICToolCallLocation = (AICMessageLocation & { toolCall: ct.AICToolCall }) | undefined;

export class Asset extends BaseObject {
  constructor(
    public id: string,
    public name: string,
    public version: string,
    public defined_in: t.MaterialDefinitionSource,
    public type: t.AssetType,
    public usage: string,
    public usage_examples: string[],
    public enabled_by_default: boolean,
    public enabled: boolean,
    public override: boolean,
    public last_modified: string,
  ) {
    super(id);
  }
}
export class AICMessageGroup extends BaseObject {
  constructor(
    id: string,
    public actor_id: ct.ActorId,
    public role: t.GPTRole = 'user',
    public task: string = '',
    public analysis: string = '',
    public messages: AICMessage[] = [],
    public materials_ids: string[] = [],
  ) {
    super(id);
  }
}

export class AICMessage extends BaseObject implements ct.AICMessage {
  constructor(
    id: string,
    public timestamp: string,
    public content: string,
    public tool_calls: ct.AICToolCall[],
    public is_streaming: boolean,
  ) {
    super(id);
  }
}

export class AICChatOptions implements ct.AICChatOptions {
  constructor(
    public agent_id: string = '',
    public materials_ids: string[] = [],
    public ai_can_add_extra_materials: boolean = true,
    public draft_command: string = '',
  ) {}

  isDefault(): boolean {
    return this.agent_id === '' && this.materials_ids.length === 0 && this.draft_command === '';
  }
}

export class AICChat extends Asset implements ct.AICChat {
  chat_options: AICChatOptions;
  type: 'chat';

  constructor(
    public title_edited: boolean,
    public message_groups: ct.AICMessageGroup[],
    public is_analysis_in_progress: boolean,
    chat_options: ConstructorParameters<typeof AICChatOptions>,
    ...args: ConstructorParameters<typeof Asset>
  ) {
    super(...args);
    this.type = 'chat';
    this.chat_options = new AICChatOptions(...chat_options);
  }

  getMessageGroup(groupId: string): ct.AICMessageGroup | undefined {
    return this.message_groups.find((group) => group.id === groupId);
  }

  getMessageLocation(messageId: string): AICMessageLocation {
    for (const group of this.message_groups) {
      const message = group.messages.find((m) => m.id === messageId);
      if (message) {
        return { group, message };
      }
    }
  }

  getToolCallLocation(toolCallId: string): AICToolCallLocation {
    for (const group of this.message_groups) {
      for (const message of group.messages) {
        const toolCall = message.tool_calls.find((tc) => tc.id === toolCallId);
        if (toolCall) {
          return { group, message, toolCall };
        }
      }
    }
  }

  static createEmptyChat() {
    return new AICChat(
      false,
      [],
      false,
      ['', [], true, ''],
      uuidv4(),
      'New Chat',
      '0.0.1',
      'aiconsole',
      'chat',
      '',
      [],
      true,
      true,
      false,
      new Date().toISOString(),
    );
  }
}

export class AICAgent extends Asset implements AICAgent {
  constructor(
    public system: string,
    public gpt_mode: t.GPTMode,
    public execution_mode: string,
    public execution_mode_params_values: Record<string, string>,
    ...args: ConstructorParameters<typeof Asset>
  ) {
    super(...args);
  }
}
