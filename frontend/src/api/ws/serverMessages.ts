// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { z } from 'zod';
import { ChatSchema } from '@/types/editables/chatTypes';
import { AssetTypeSchema } from '@/types/editables/assetTypes';
import { ChatMutationSchema } from './chat/chatMutations';

export const BaseServerMessageSchema = z.object({});

export type BaseServerMessage = z.infer<typeof BaseServerMessageSchema>;

export const NotificationServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('NotificationServerMessage'),
  title: z.string(),
  message: z.string(),
});

export type NotificationServerMessage = z.infer<typeof NotificationServerMessageSchema>;

export const DebugJSONServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('DebugJSONServerMessage'),
  message: z.string(),
  object: z.record(z.string(), z.any()), // Assuming `object` is a simple dictionary
});

export type DebugJSONServerMessage = z.infer<typeof DebugJSONServerMessageSchema>;

export const ErrorServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('ErrorServerMessage'),
  error: z.string(),
});

export type ErrorServerMessage = z.infer<typeof ErrorServerMessageSchema>;

export const InitialProjectStatusServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('InitialProjectStatusServerMessage'),
  project_name: z.string().optional(),
  project_path: z.string().optional(),
});

export type InitialProjectStatusServerMessage = z.infer<typeof InitialProjectStatusServerMessageSchema>;

export const ProjectOpenedServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('ProjectOpenedServerMessage'),
  name: z.string(),
  path: z.string(),
});

export type ProjectOpenedServerMessage = z.infer<typeof ProjectOpenedServerMessageSchema>;

export const ProjectClosedServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('ProjectClosedServerMessage'),
});

export type ProjectClosedServerMessage = z.infer<typeof ProjectClosedServerMessageSchema>;

export const ProjectLoadingServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('ProjectLoadingServerMessage'),
});

export type ProjectLoadingServerMessage = z.infer<typeof ProjectLoadingServerMessageSchema>;

export const AssetsUpdatedServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('AssetsUpdatedServerMessage'),
  initial: z.boolean(),
  asset_type: AssetTypeSchema, // Assuming Asset is an enum
  count: z.number(),
});

export type AssetsUpdatedServerMessage = z.infer<typeof AssetsUpdatedServerMessageSchema>;

export const SettingsServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('SettingsServerMessage'),
  initial: z.boolean(),
});

export type SettingsServerMessage = z.infer<typeof SettingsServerMessageSchema>;

export const NotifyAboutChatMutationServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('NotifyAboutChatMutationServerMessage'),
  request_id: z.string(),
  chat_id: z.string(),
  mutation: ChatMutationSchema, // Assuming ChatMutationSchema is defined
});

export type NotifyAboutChatMutationServerMessage = z.infer<typeof NotifyAboutChatMutationServerMessageSchema>;

export const ChatOpenedServerMessageSchema = BaseServerMessageSchema.extend({
  type: z.literal('ChatOpenedServerMessage'),
  chat: ChatSchema,
});

export type ChatOpenedServerMessage = z.infer<typeof ChatOpenedServerMessageSchema>;

export const ServerMessageSchema = z.union([
  NotificationServerMessageSchema,
  DebugJSONServerMessageSchema,
  ErrorServerMessageSchema,
  InitialProjectStatusServerMessageSchema,
  ProjectOpenedServerMessageSchema,
  ProjectClosedServerMessageSchema,
  ProjectLoadingServerMessageSchema,
  AssetsUpdatedServerMessageSchema,
  SettingsServerMessageSchema,
  NotifyAboutChatMutationServerMessageSchema,
  ChatOpenedServerMessageSchema,
]);

export type ServerMessage = z.infer<typeof ServerMessageSchema>;
