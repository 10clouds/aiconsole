import { z } from 'zod';
import { ObjectRefSchema } from '@/types/assets/assetTypes';
import { BaseObject, CollectionRef, ObjectRef } from '@/store/assets/types';

export const BaseMutationSchema = z.object({
  ref: ObjectRefSchema,
});

// export type BaseMutation = z.infer<typeof BaseMutationSchema>;

export interface BaseMutation {
  ref: ObjectRef | CollectionRef;
}

export const CreateMutationSchema = BaseMutationSchema.extend({
  type: z.literal('CreateMutation'),
  object_type: z.string(),
  object: z.record(z.string(), z.any()),
});

// export type CreateMutation = z.infer<typeof CreateMutationSchema>;

export interface CreateMutation<T extends BaseObject> extends BaseMutation {
  ref: ObjectRef;
  type: 'CreateMutation';
  object_type: string;
  object: T;
}

export const DeleteMutationSchema = BaseMutationSchema.extend({
  type: z.literal('DeleteMutation'),
});

// export type DeleteMutation = z.infer<typeof DeleteMutationSchema>;

export interface DeleteMutation extends BaseMutation {
  ref: ObjectRef;
  type: 'DeleteMutation';
}

export const SetValueMutationSchema = BaseMutationSchema.extend({
  type: z.literal('SetValueMutation'),
  key: z.string(),
  value: z.any().optional().default(null),
});

// export type SetValueMutation = z.infer<typeof SetValueMutationSchema>;

export interface SetValueMutation extends BaseMutation {
  ref: ObjectRef;
  type: 'SetValueMutation';
  key: string;
  value: unknown;
}

export const AppendToStringMutationSchema = BaseMutationSchema.extend({
  type: z.literal('AppendToStringMutation'),
  key: z.string(),
  value: z.string(),
});

// export type AppendToStringMutation = z.infer<typeof AppendToStringMutationSchema>;

export interface AppendToStringMutation extends BaseMutation {
  type: 'AppendToStringMutation';
  key: string;
  value: string;
}

export const AssetMutationSchema = z.discriminatedUnion('type', [
  CreateMutationSchema,
  DeleteMutationSchema,
  SetValueMutationSchema,
  AppendToStringMutationSchema,
]);

// export type AssetMutation = z.infer<typeof AssetMutationSchema>;

export type AssetMutation<T extends BaseObject> =
  | CreateMutation<T>
  | DeleteMutation
  | SetValueMutation
  | AppendToStringMutation;
