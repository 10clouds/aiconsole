import { z } from 'zod';
import { AssetSchema, GPTRoleSchema } from './assetTypes'; // Import necessary types and schemas

export const AICToolCallSchema = z.object({
  id: z.string(),
  language: z.string().optional(),
  code: z.string(),
  headline: z.string(),
  output: z.string().optional(),
  is_successful: z.boolean(),
  is_executing: z.boolean(),
  is_streaming: z.boolean(),
});

export type AICToolCall = z.infer<typeof AICToolCallSchema>;

export const AICMessageSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  content: z.string(),
  tool_calls: z.array(AICToolCallSchema),
  is_streaming: z.boolean(),
});

export const ActorIdSchema = z.object({
  type: z.enum(['user', 'agent']),
  id: z.string(),
});

export type ActorId = z.infer<typeof ActorIdSchema>;

export type AICMessage = z.infer<typeof AICMessageSchema>;

export const AICMessageGroupSchema = z.object({
  id: z.string(),
  actor_id: ActorIdSchema,
  role: GPTRoleSchema,
  task: z.string(),
  materials_ids: z.array(z.string()),
  messages: z.array(AICMessageSchema),
  analysis: z.string(),
});

export type AICMessageGroup = z.infer<typeof AICMessageGroupSchema>;

export const AICChatHeadlineSchema = AssetSchema.extend({});

export type AICChatHeadline = z.infer<typeof AICChatHeadlineSchema>;

const AICChatOptionsSchema = z.object({
  agent_id: z.string().optional().default(''),
  materials_ids: z.array(z.string()).default([]),
  ai_can_add_extra_materials: z.boolean().default(true),
  draft_command: z.string().default(''),
});

export type AICChatOptions = z.infer<typeof AICChatOptionsSchema>;

export const AICChatSchema = AssetSchema.extend({
  lock_id: z.string().optional(),
  title_edited: z.boolean(),
  chat_options: AICChatOptionsSchema,
  message_groups: z.array(AICMessageGroupSchema),
  is_analysis_in_progress: z.boolean(),
});

export type AICChat = z.infer<typeof AICChatSchema>;

// Helper functions

export function createDefaultChatOptions(): AICChatOptions {
  return {
    agent_id: '',
    materials_ids: [],
    ai_can_add_extra_materials: true,
    draft_command: '',
  };
}

export function createEmptyChat(): AICChat {
  return {
    id: 'new',
    type: 'chat',
    name: 'New Chat',
    version: '0.0.1',
    usage: '',
    usage_examples: [],
    override: false,
    last_modified: new Date().toISOString(),
    defined_in: 'project',
    enabled: true,
    enabled_by_default: true,
    lock_id: undefined,
    title_edited: false,
    chat_options: createDefaultChatOptions(),
    message_groups: [],
    is_analysis_in_progress: false,
  };
}

// Helper functions

export function getMessageGroup(chat: AICChat, message_group_id: string) {
  for (const group of chat.message_groups) {
    if (group.id === message_group_id) {
      return group;
    }
  }
  throw new Error(`Message group ${message_group_id} not found`);
}

export function getMessageLocation(chat: AICChat, message_id: string) {
  for (const group of chat.message_groups) {
    for (const message of group.messages) {
      if (message.id === message_id) {
        return {
          group,
          message,
        };
      }
    }
  }
  throw new Error(`Message ${message_id} not found`);
}

export function getToolCallLocation(chat: AICChat, tool_call_id: string) {
  for (const group of chat.message_groups) {
    for (const message of group.messages) {
      for (const tool_call of message.tool_calls) {
        if (tool_call.id === tool_call_id) {
          return {
            group,
            message,
            tool_call,
          };
        }
      }
    }
  }
  throw new Error(`Tool call ${tool_call_id} not found`);
}
