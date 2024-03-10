import { GPTRoleSchema, LanguageStrSchema } from '@/types/assets/assetTypes';
import { ActorIdSchema } from '@/types/assets/chatTypes';
import { z } from 'zod';

export const LockAcquiredMutationSchema = z.object({
  type: z.literal('LockAcquiredMutation'),
  lock_id: z.string(),
});

export type LockAcquiredMutation = z.infer<typeof LockAcquiredMutationSchema>;

export const LockReleasedMutationSchema = z.object({
  type: z.literal('LockReleasedMutation'),
  lock_id: z.string(),
});

export type LockReleasedMutation = z.infer<typeof LockReleasedMutationSchema>;

export const DuplicateAssetClientMessageSchema = z.object({
  type: z.literal('DuplicateAssetClientMessage'),
  asset_id: z.string(),
  request_id: z.string(),
});

export type DuplicateAssetClientMessage = z.infer<typeof DuplicateAssetClientMessageSchema>;

export const CreateMessageGroupMutationSchema = z.object({
  type: z.literal('CreateMessageGroupMutation'),
  message_group_id: z.string(),
  actor_id: ActorIdSchema,
  role: GPTRoleSchema, // Replace with actual GPTRole schema
  task: z.string(),
  materials_ids: z.array(z.string()),
  analysis: z.string(),
});

export type CreateMessageGroupMutation = z.infer<typeof CreateMessageGroupMutationSchema>;

export const DeleteMessageGroupMutationSchema = z.object({
  type: z.literal('DeleteMessageGroupMutation'),
  message_group_id: z.string(),
});

export type DeleteMessageGroupMutation = z.infer<typeof DeleteMessageGroupMutationSchema>;

export const SetIsAnalysisInProgressMutationSchema = z.object({
  type: z.literal('SetIsAnalysisInProgressMutation'),
  is_analysis_in_progress: z.boolean(),
});

export type SetIsAnalysisInProgressMutation = z.infer<typeof SetIsAnalysisInProgressMutationSchema>;

export const SetTaskMessageGroupMutationSchema = z.object({
  type: z.literal('SetTaskMessageGroupMutation'),
  message_group_id: z.string(),
  task: z.string(),
});

export type SetTaskMessageGroupMutation = z.infer<typeof SetTaskMessageGroupMutationSchema>;

export const AppendToTaskMessageGroupMutationSchema = z.object({
  type: z.literal('AppendToTaskMessageGroupMutation'),
  message_group_id: z.string(),
  task_delta: z.string(),
});

export type AppendToTaskMessageGroupMutation = z.infer<typeof AppendToTaskMessageGroupMutationSchema>;

export const SetRoleMessageGroupMutationSchema = z.object({
  type: z.literal('SetRoleMessageGroupMutation'),
  message_group_id: z.string(),
  role: GPTRoleSchema, // Replace with actual GPTRole schema
});

export type SetRoleMessageGroupMutation = z.infer<typeof SetRoleMessageGroupMutationSchema>;

export const SetActorIdMessageGroupMutationSchema = z.object({
  type: z.literal('SetActorIdMessageGroupMutation'),
  message_group_id: z.string(),
  actor_id: ActorIdSchema,
});

export type SetActorIdMessageGroupMutation = z.infer<typeof SetActorIdMessageGroupMutationSchema>;

export const SetMaterialsIdsMessageGroupMutationSchema = z.object({
  type: z.literal('SetMaterialsIdsMessageGroupMutation'),
  message_group_id: z.string(),
  materials_ids: z.array(z.string()),
});

export type SetMaterialsIdsMessageGroupMutation = z.infer<typeof SetMaterialsIdsMessageGroupMutationSchema>;

export const AppendToMaterialsIdsMessageGroupMutationSchema = z.object({
  type: z.literal('AppendToMaterialsIdsMessageGroupMutation'),
  message_group_id: z.string(),
  material_id: z.string(),
});

export type AppendToMaterialsIdsMessageGroupMutation = z.infer<typeof AppendToMaterialsIdsMessageGroupMutationSchema>;

export const SetAnalysisMessageGroupMutationSchema = z.object({
  type: z.literal('SetAnalysisMessageGroupMutation'),
  message_group_id: z.string(),
  analysis: z.string(),
});

export type SetAnalysisMessageGroupMutation = z.infer<typeof SetAnalysisMessageGroupMutationSchema>;

export const AppendToAnalysisMessageGroupMutationSchema = z.object({
  type: z.literal('AppendToAnalysisMessageGroupMutation'),
  message_group_id: z.string(),
  analysis_delta: z.string(),
});

export type AppendToAnalysisMessageGroupMutation = z.infer<typeof AppendToAnalysisMessageGroupMutationSchema>;

export const DeleteToolCallMutationSchema = z.object({
  type: z.literal('DeleteToolCallMutation'),
  tool_call_id: z.string(),
});

export type DeleteToolCallMutation = z.infer<typeof DeleteToolCallMutationSchema>;

export const SetHeadlineToolCallMutationSchema = z.object({
  type: z.literal('SetHeadlineToolCallMutation'),
  tool_call_id: z.string(),
  headline: z.string(),
});

export type SetHeadlineToolCallMutation = z.infer<typeof SetHeadlineToolCallMutationSchema>;

export const AppendToHeadlineToolCallMutationSchema = z.object({
  type: z.literal('AppendToHeadlineToolCallMutation'),
  tool_call_id: z.string(),
  headline_delta: z.string(),
});

export type AppendToHeadlineToolCallMutation = z.infer<typeof AppendToHeadlineToolCallMutationSchema>;

export const SetCodeToolCallMutationSchema = z.object({
  type: z.literal('SetCodeToolCallMutation'),
  tool_call_id: z.string(),
  code: z.string(),
});

export type SetCodeToolCallMutation = z.infer<typeof SetCodeToolCallMutationSchema>;

export const AppendToCodeToolCallMutationSchema = z.object({
  type: z.literal('AppendToCodeToolCallMutation'),
  tool_call_id: z.string(),
  code_delta: z.string(),
});

export type AppendToCodeToolCallMutation = z.infer<typeof AppendToCodeToolCallMutationSchema>;

export const SetLanguageToolCallMutationSchema = z.object({
  type: z.literal('SetLanguageToolCallMutation'),
  tool_call_id: z.string(),
  language: LanguageStrSchema, // Replace with actual LanguageStr schema
});

export type SetLanguageToolCallMutation = z.infer<typeof SetLanguageToolCallMutationSchema>;

export const SetOutputToolCallMutationSchema = z.object({
  type: z.literal('SetOutputToolCallMutation'),
  tool_call_id: z.string(),
  output: z.string().optional(),
});

export type SetOutputToolCallMutation = z.infer<typeof SetOutputToolCallMutationSchema>;

export const AppendToOutputToolCallMutationSchema = z.object({
  type: z.literal('AppendToOutputToolCallMutation'),
  tool_call_id: z.string(),
  output_delta: z.string(),
});

export type AppendToOutputToolCallMutation = z.infer<typeof AppendToOutputToolCallMutationSchema>;

export const SetIsSuccessfulToolCallMutationSchema = z.object({
  type: z.literal('SetIsSuccessfulToolCallMutation'),
  tool_call_id: z.string(),
  is_successful: z.boolean(),
});

export type SetHasErrorToolCallMutation = z.infer<typeof SetIsSuccessfulToolCallMutationSchema>;

export const SetIsStreamingToolCallMutationSchema = z.object({
  type: z.literal('SetIsStreamingToolCallMutation'),
  tool_call_id: z.string(),
  is_streaming: z.boolean(),
});

export type SetIsStreamingToolCallMutation = z.infer<typeof SetIsStreamingToolCallMutationSchema>;

export const SetIsExecutingToolCallMutationSchema = z.object({
  type: z.literal('SetIsExecutingToolCallMutation'),
  tool_call_id: z.string(),
  is_executing: z.boolean(),
});

export type SetIsExecutingToolCallMutation = z.infer<typeof SetIsExecutingToolCallMutationSchema>;

export const CreateMessageMutationSchema = z.object({
  type: z.literal('CreateMessageMutation'),
  message_group_id: z.string(),
  message_id: z.string(),
  timestamp: z.string(),
  content: z.string(),
});

export type CreateMessageMutation = z.infer<typeof CreateMessageMutationSchema>;

export const DeleteMessageMutationSchema = z.object({
  type: z.literal('DeleteMessageMutation'),
  message_id: z.string(),
});

export type DeleteMessageMutation = z.infer<typeof DeleteMessageMutationSchema>;

export const AppendToContentMessageMutationSchema = z.object({
  type: z.literal('AppendToContentMessageMutation'),
  message_id: z.string(),
  content_delta: z.string(),
});

export type AppendToContentMessageMutation = z.infer<typeof AppendToContentMessageMutationSchema>;

export const SetContentMessageMutationSchema = z.object({
  type: z.literal('SetContentMessageMutation'),
  message_id: z.string(),
  content: z.string(),
});

export type SetContentMessageMutation = z.infer<typeof SetContentMessageMutationSchema>;

export const SetIsStreamingMessageMutationSchema = z.object({
  type: z.literal('SetIsStreamingMessageMutation'),
  message_id: z.string(),
  is_streaming: z.boolean(),
});

export type SetIsStreamingMessageMutation = z.infer<typeof SetIsStreamingMessageMutationSchema>;

export const CreateToolCallMutationSchema = z.object({
  type: z.literal('CreateToolCallMutation'),
  message_id: z.string(),
  tool_call_id: z.string(),
  code: z.string(),
  headline: z.string(),
  output: z.string().optional(),
  language: LanguageStrSchema.optional(),
  is_successful: z.boolean(),
  is_streaming: z.boolean(),
  is_executing: z.boolean(),
});

export const ChatMutationSchema = z.union([
  LockAcquiredMutationSchema,
  LockReleasedMutationSchema,
  CreateMessageGroupMutationSchema,
  DeleteMessageGroupMutationSchema,
  SetIsAnalysisInProgressMutationSchema,
  SetTaskMessageGroupMutationSchema,
  AppendToTaskMessageGroupMutationSchema,
  SetRoleMessageGroupMutationSchema,
  SetActorIdMessageGroupMutationSchema,
  SetMaterialsIdsMessageGroupMutationSchema,
  AppendToMaterialsIdsMessageGroupMutationSchema,
  SetAnalysisMessageGroupMutationSchema,
  AppendToAnalysisMessageGroupMutationSchema,
  CreateMessageMutationSchema,
  DeleteMessageMutationSchema,
  AppendToContentMessageMutationSchema,
  SetContentMessageMutationSchema,
  SetIsStreamingMessageMutationSchema,
  CreateToolCallMutationSchema,
  DeleteToolCallMutationSchema,
  SetHeadlineToolCallMutationSchema,
  AppendToHeadlineToolCallMutationSchema,
  SetCodeToolCallMutationSchema,
  AppendToCodeToolCallMutationSchema,
  SetLanguageToolCallMutationSchema,
  SetOutputToolCallMutationSchema,
  AppendToOutputToolCallMutationSchema,
  SetIsSuccessfulToolCallMutationSchema,
  SetIsStreamingToolCallMutationSchema,
  SetIsExecutingToolCallMutationSchema,
]);

export type ChatMutation = z.infer<typeof ChatMutationSchema>;
