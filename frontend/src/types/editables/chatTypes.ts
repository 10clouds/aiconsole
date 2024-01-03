import { z } from 'zod';
import { EditableObjectSchema, GPTRoleSchema } from './assetTypes'; // Import necessary types and schemas

export const AICToolCallSchema = z.object({
  id: z.string(),
  language: z.string().optional(),
  is_executing: z.boolean(),
  is_streaming: z.boolean(),
  code: z.string(),
  headline: z.string(),
  output: z.string().optional(),
});

export type AICToolCall = z.infer<typeof AICToolCallSchema>;

export const AICMessageSchema = z.object({
  id: z.string(),
  timestamp: z.string(),
  content: z.string(),
  tool_calls: z.array(AICToolCallSchema),
  is_streaming: z.boolean(),
});

export type AICMessage = z.infer<typeof AICMessageSchema>;

export const AICMessageGroupSchema = z.object({
  id: z.string(),
  agent_id: z.string(),
  username: z.string().optional(),
  email: z.string().optional(),
  role: GPTRoleSchema,
  task: z.string(),
  materials_ids: z.array(z.string()),
  messages: z.array(AICMessageSchema),
  analysis: z.string(),
});

export type AICMessageGroup = z.infer<typeof AICMessageGroupSchema>;

export const ChatHeadlineSchema = EditableObjectSchema.extend({
  last_modified: z.string(),
});

export type ChatHeadline = z.infer<typeof ChatHeadlineSchema>;

export const ChatSchema = EditableObjectSchema.extend({
  lock_id: z.string().optional(),
  title_edited: z.boolean(),
  last_modified: z.string(),
  message_groups: z.array(AICMessageGroupSchema),
  is_analysis_in_progress: z.boolean(),
});

export type Chat = z.infer<typeof ChatSchema>;

// Helper functions

export function getMessageGroup(chat: Chat, message_group_id: string) {
  for (const group of chat.message_groups) {
    if (group.id === message_group_id) {
      return group;
    }
  }
  throw new Error(`Message group ${message_group_id} not found`);
}

export function getMessageLocation(chat: Chat, message_id: string) {
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

export function getToolCallLocation(chat: Chat, tool_call_id: string) {
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
