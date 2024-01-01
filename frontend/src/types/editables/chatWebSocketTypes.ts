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

import { GPTRole } from './assetTypes';

export type RequestProcessingFinishedWSMessage = {
  type: 'RequestProcessingFinishedWSMessage';
  request_id: string;
  aborted: boolean;
};

export type ChatMutationWSMessage = {
  request_id: string;
  chat_id: string;
};

export type OpCreateMessageGroupWSMessage = ChatMutationWSMessage & {
  type: 'OpCreateMessageGroupWSMessage';
  message_group_id: string;
  agent_id: string;
  role: GPTRole;
  task: string;
  materials_ids: string[];
  analysis: string;
};

export type OpDeleteMessageGroupWSMessage = ChatMutationWSMessage & {
  type: 'OpDeleteMessageGroupWSMessage';
  message_group_id: string;
};

export type OpSetIsAnalysisInProgressWSMessage = ChatMutationWSMessage & {
  type: 'OpSetIsAnalysisInProgressWSMessage';
  is_analysis_in_progress: boolean;
};

// Message Groups - Task

export type OpSetMessageGroupTaskWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageGroupTaskWSMessage';
  message_group_id: string;
  task: string;
};

export type OpAppendToMessageGroupTaskWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToMessageGroupTaskWSMessage';
  message_group_id: string;
  task_delta: string;
};

// Message Groups - Role

export type OpSetMessageGroupRoleWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageGroupRoleWSMessage';
  message_group_id: string;
  role: GPTRole;
};

export type OpSetMessageGroupAgentIdWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageGroupAgentIdWSMessage';
  message_group_id: string;
  agent_id: string;
};

// Message Groups - Materials

export type OpSetMessageGroupMaterialsIdsWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageGroupMaterialsIdsWSMessage';
  message_group_id: string;
  materials_ids: string[];
};

export type OpAppendToMessageGroupMaterialsIdsWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToMessageGroupMaterialsIdsWSMessage';
  message_group_id: string;
  material_id: string;
};

// Message Groups - Analysis

export type OpSetMessageGroupAnalysisWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageGroupAnalysisWSMessage';
  message_group_id: string;
  analysis: string;
};

export type OpAppendToMessageGroupAnalysisWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToMessageGroupAnalysisWSMessage';
  message_group_id: string;
  analysis_delta: string;
};

// Messages

export type OpCreateMessageWSMessage = ChatMutationWSMessage & {
  type: 'OpCreateMessageWSMessage';
  message_group_id: string;
  message_id: string;
  timestamp: string;
  content: string;
};

export type OpDeleteMessageWSMessage = ChatMutationWSMessage & {
  type: 'OpDeleteMessageWSMessage';
  message_id: string;
};

// Messages - Content

export type OpAppendToMessageContentWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToMessageContentWSMessage';
  message_id: string;
  content_delta: string;
};

export type OpSetMessageContentWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageContentWSMessage';
  message_id: string;
  content: string;
};

// Messages - Is streaming

export type OpSetMessageIsStreamingWSMessage = ChatMutationWSMessage & {
  type: 'OpSetMessageIsStreamingWSMessage';
  message_id: string;
  is_streaming: boolean;
};

// Tool Calls

export type OpCreateToolCallWSMessage = ChatMutationWSMessage & {
  type: 'OpCreateToolCallWSMessage';
  message_id: string;
  tool_call_id: string;
  code: string;
  language: string;
  headline: string;
  output: string | null;
};

export type OpDeleteToolCallWSMessage = ChatMutationWSMessage & {
  type: 'OpDeleteToolCallWSMessage';
  tool_call_id: string;
};

// Tool Calls - Headline

export type OpSetToolCallHeadlineWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallHeadlineWSMessage';
  tool_call_id: string;
  headline: string;
};

export type OpAppendToToolCallHeadlineWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToToolCallHeadlineWSMessage';
  tool_call_id: string;
  headline_delta: string;
};

// Tool Calls - Code

export type OpSetToolCallCodeWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallCodeWSMessage';
  tool_call_id: string;
  code: string;
};

export type OpAppendToToolCallCodeWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToToolCallCodeWSMessage';
  tool_call_id: string;
  code_delta: string;
};

// Tool Calls - Language

export type OpSetToolCallLanguageWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallLanguageWSMessage';
  tool_call_id: string;
  language: string;
};

// Tool Calls - Output

export type OpSetToolCallOutputWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallOutputWSMessage';
  tool_call_id: string;
  output: string | null;
};

export type OpAppendToToolCallOutputWSMessage = ChatMutationWSMessage & {
  type: 'OpAppendToToolCallOutputWSMessage';
  tool_call_id: string;
  output_delta: string;
};

// Tool Calls - Is streaming

export type OpSetToolCallIsStreamingWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallIsStreamingWSMessage';
  tool_call_id: string;
  is_streaming: boolean;
};

export type OpSetToolCallIsExecutingWSMessage = ChatMutationWSMessage & {
  type: 'OpSetToolCallIsExecutingWSMessage';
  tool_call_id: string;
  is_executing: boolean;
};

export type ChatWSMessage =
  | OpCreateMessageGroupWSMessage
  | OpDeleteMessageGroupWSMessage
  | OpSetIsAnalysisInProgressWSMessage
  | OpSetMessageGroupTaskWSMessage
  | OpAppendToMessageGroupTaskWSMessage
  | OpSetMessageGroupRoleWSMessage
  | OpSetMessageGroupAgentIdWSMessage
  | OpSetMessageGroupMaterialsIdsWSMessage
  | OpAppendToMessageGroupMaterialsIdsWSMessage
  | OpSetMessageGroupAnalysisWSMessage
  | OpAppendToMessageGroupAnalysisWSMessage
  | OpCreateMessageWSMessage
  | OpDeleteMessageWSMessage
  | OpAppendToMessageContentWSMessage
  | OpSetMessageContentWSMessage
  | OpSetMessageIsStreamingWSMessage
  | OpCreateToolCallWSMessage
  | OpDeleteToolCallWSMessage
  | OpSetToolCallHeadlineWSMessage
  | OpAppendToToolCallHeadlineWSMessage
  | OpSetToolCallCodeWSMessage
  | OpAppendToToolCallCodeWSMessage
  | OpSetToolCallLanguageWSMessage
  | OpSetToolCallOutputWSMessage
  | OpAppendToToolCallOutputWSMessage
  | OpSetToolCallIsStreamingWSMessage
  | OpSetToolCallIsExecutingWSMessage;
