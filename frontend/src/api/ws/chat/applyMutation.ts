import { useTTSStore } from '@/audio/useTTSStore';
import { AICChatOptions, Asset } from '@/store/assets/constructors';
import { BaseObject } from '@/store/assets/types';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { MessageBuffer } from '@/utils/common/MessageBuffer';
import {
  AppendToStringMutation,
  AssetMutation,
  CreateMutation,
  DeleteMutation,
  SetValueMutation,
} from '../assetMutations';
import { DataContext } from '@/store/assets/DataContext';

function findAttribute<T extends BaseObject>(asset: Asset | null, mutation: AssetMutation<T>): T | T[] | null {
  let attr = asset as BaseObject as T | T[] | null;

  for (const ref of mutation.ref.ref_segments.slice(2, -1)) {
    if (Array.isArray(attr)) {
      const index = attr.findIndex((a) => a.id === ref);
      attr = attr[index] as T;
    } else {
      attr = attr![ref as keyof typeof attr] as T[];
    }
  }

  return attr;
}

function handleCreateMutation<T extends BaseObject>(context: DataContext, mutation: CreateMutation<T>): void {
  const collection = context.get(mutation.ref.parent_collection) as T[] | null;

  if (!collection) {
    throw new Error(`Collection ${mutation.ref} not found`);
  }

  const asset = useAssetStore.getState().assets.find((a) => a.id === mutation.ref.ref_segments[1]) ?? null; // [0] is 'assets' and [1] is the asset id

  const obj = mutation.object;

  let attr = findAttribute(asset, mutation);

  if (Array.isArray(attr)) {
    attr.push(obj);
  } else if (typeof attr === 'object' && attr !== null) {
    Object.assign(attr, obj);
  } else {
    attr = obj;
  }

  useAssetStore.getState().saveAsset(asset ?? (obj as unknown as Asset));
}

function handleDeleteMutation<T extends BaseObject>(context: DataContext, mutation: DeleteMutation): void {
  const collection = context.get(mutation.ref.parent_collection) as T[];

  if (collection === null) {
    throw new Error(`Collection ${mutation.ref.parent_collection} not found`);
  }

  const asset = useAssetStore.getState().assets.find((a) => a.id === mutation.ref.ref_segments[1]) ?? null;

  if (asset === null) {
    throw new Error(`Asset ${mutation.ref.ref_segments[1]} not found`);
  }

  const obj = context.get(mutation.ref) as BaseObject;

  if (obj === null) {
    throw new Error(`Object ${mutation.ref} not found`);
  }

  const objIndex = collection.findIndex((item) => item.id === obj.id);
  collection.splice(objIndex, 1);

  useAssetStore.setState((state) => ({
    ...state,
    assets: [...state.assets.filter((item) => item.id !== asset.id), asset],
  }));
}

function handleSetValueMutation(context: DataContext, mutation: SetValueMutation): void {
  const asset = useAssetStore.getState().assets.find((a) => a.id === mutation.ref.ref_segments[1]) ?? null;

  if (asset === null) {
    throw new Error(`Asset ${mutation.ref.ref_segments[1]} not found`);
  }

  const attr = findAttribute(asset, mutation) as unknown as Record<string, any>;

  const { value, key } = mutation;

  if (attr !== null && typeof attr === 'object') {
    if (attr[key] instanceof AICChatOptions) {
      const { agent_id, ai_can_add_extra_materials, draft_command, materials_ids } = attr[key] as AICChatOptions;
      attr[key] = new AICChatOptions(agent_id, materials_ids, ai_can_add_extra_materials, draft_command);
    } else {
      attr[key] = value;
    }
  }

  useAssetStore.setState((state) => ({
    ...state,
    assets: [...state.assets.filter((item) => item.id !== asset.id), asset],
  }));

  // Finish playing speech if content has finished changing
  // Should probably be added externally as an additional handler for is_streaming (using some kind of staticlly typed ref?)
  if (key === 'is_streaming' && !value) {
    useTTSStore.getState().readText(attr['content'], false);
  }
}

function handleAppendToStringMutation(context: DataContext, mutation: AppendToStringMutation): void {
  const asset = useAssetStore.getState().assets.find((a) => a.id === mutation.ref.ref_segments[1]) ?? null;

  if (asset === null) {
    throw new Error(`Asset ${mutation.ref.ref_segments[1]} not found`);
  }

  const attr = findAttribute(asset, mutation) as unknown as Record<string, any>;

  const { value, key } = mutation;

  if (attr !== null && typeof attr === 'object') {
    attr[key] = attr[key] + value;
  }

  useAssetStore.setState((state) => ({
    ...state,
    assets: [...state.assets.filter((item) => item.id !== asset.id), asset],
  }));

  // Play Speech if content is changed
  // Should probably be added externally as an additional handler for is_streaming (using some kind of staticlly typed ref?)
  if (useTTSStore.getState().hasAutoPlay && key === 'content') {
    useTTSStore.getState().readText(attr[key], true);
  }
}

export function applyMutation<T extends BaseObject>(
  context: DataContext,
  mutation: AssetMutation<T>,
  messageBuffer?: MessageBuffer,
) {
  switch (mutation.type) {
    case 'CreateMutation':
      handleCreateMutation<T>(context, mutation);
      break;
    case 'DeleteMutation':
      handleDeleteMutation(context, mutation);
      break;
    case 'SetValueMutation': {
      handleSetValueMutation(context, mutation);
      break;
    }
    case 'AppendToStringMutation':
      handleAppendToStringMutation(context, mutation);
      break;
  }
}
