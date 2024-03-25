import { useTTSStore } from '@/audio/useTTSStore';
import { Asset } from '@/types/assets/assetTypes';
import { AICChat } from '@/types/assets/chatTypes';
import { getRefSegments } from '@/utils/assets/getRefSegments';
import { MessageBuffer } from '@/utils/common/MessageBuffer';
import {
  AppendToStringMutation,
  AssetMutation,
  CreateMutation,
  DeleteMutation,
  SetValueMutation,
} from '../assetMutations';

type Attr = Record<string, unknown> | undefined | null | Array<Record<string, unknown>>;

function findAttribute(asset: Asset | AICChat, refSegments: string[]): Attr {
  let attr = asset;
  for (const refSegment of refSegments.slice(2, -1)) {
    if (Array.isArray(attr)) {
      const index = attr.findIndex((a) => a.id === refSegment);
      attr = attr[index];
    } else {
      attr = (attr as any)[refSegment];
    }
  }
  return attr;
}

function handleCreateMutation(asset: Asset | AICChat, mutation: CreateMutation): void {
  const { refSegments } = mutation.ref;
  let attr = findAttribute(asset, refSegments);
  const object = mutation.object;
  if (object.id === undefined) {
    object.id = mutation.ref.id;
  }
  if (Array.isArray(attr)) {
    attr.push(object);
  } else if (typeof attr === 'object' && attr !== null) {
    Object.assign(attr, object);
  } else {
    attr = object;
  }
}

function handleDeleteMutation(asset: Asset | AICChat, mutation: DeleteMutation): void {
  const collection = findAttribute(asset, mutation.ref.refSegments);

  if (Array.isArray(collection)) {
    const index = collection.findIndex((a) => a?.id === mutation.ref.id);
    collection.splice(index, 1);
  }
}

function handleSetValueMutation(asset: Asset | AICChat, mutation: SetValueMutation): void {
  const { key, value } = mutation;
  const { refSegments } = mutation.ref;
  const attr = findAttribute(asset, refSegments) as Record<string, unknown>;
  const assetToChange = Array.isArray(attr) ? attr.find((a) => a.id === mutation.ref.id) : attr;
  assetToChange[key] = value;

  // Finish playing speech if content has finished changing
  // Should probably be added externally as an additional handler for is_streaming (using some kind of staticlly typed ref?)
  if (useTTSStore.getState().hasAutoPlay && key === 'is_streaming' && !value) {
    useTTSStore.getState().readText(assetToChange['content'], false);
  }
}

function handleAppendToStringMutation(asset: Asset | AICChat, mutation: AppendToStringMutation): void {
  const { key, value } = mutation;
  const { refSegments } = mutation.ref;
  const attr = findAttribute(asset, refSegments) as Record<string, unknown>;
  const assetToChange = Array.isArray(attr) ? attr.find((a) => a.id === mutation.ref.id) : attr;
  assetToChange[key] = (assetToChange[key] as string) + value;

  // Play Speech if content is changed
  // Should probably be added externally as an additional handler for is_streaming (using some kind of staticlly typed ref?)
  if (useTTSStore.getState().hasAutoPlay && key === 'content') {
    useTTSStore.getState().readText(assetToChange[key], true);
  }
}

export function applyMutation(asset: Asset | AICChat, mutation: AssetMutation, messageBuffer?: MessageBuffer) {
  const mutationsHandlers = {
    CreateMutation: handleCreateMutation,
    DeleteMutation: handleDeleteMutation,
    SetValueMutation: handleSetValueMutation,
    AppendToStringMutation: handleAppendToStringMutation,
  };

  const mutationType = mutation.type;

  if (mutationType in mutationsHandlers) {
    mutation.ref.refSegments = getRefSegments(mutation.ref);
    mutationsHandlers[mutationType](asset, mutation as any);
    delete mutation.ref.refSegments;
  } else {
    console.error('Unknown mutation type: ', mutation);
  }
}
