import { Asset, ObjectRef } from '@/types/assets/assetTypes';
import { v4 as uuidv4 } from 'uuid';
import {
  AppendToStringMutation,
  AssetMutation,
  CreateMutation,
  DeleteMutation,
  SetValueMutation,
} from '../ws/assetMutations';
import { applyMutation } from '../ws/chat/applyMutation';
import { useWebSocketStore } from '../ws/useWebSocketStore';
import { ClientMessage } from '../ws/clientMessages';

const ObjectTypesMap = new Map<string, string>([
  ['agent', 'AICAgent'],
  ['chat', 'AICChat'],
  ['material', 'AICMaterial'],
  ['user', 'AICUserProfile'],
  ['message_groups', 'AICMessageGroup'],
  ['messages', 'AICMessage'],
]);

export class MutationsAPI {
  private static getRef(path: string[]): ObjectRef {
    return {
      id: path[path.length - 1],
      parent_collection: {
        id: path[path.length - 2],
        parent: path.length > 2 ? this.getRef(path.slice(0, -2)) : null,
      },
    };
  }

  private static getObjectType(asset: Asset, path: string[]): string {
    if (path.length === 0) {
      return ObjectTypesMap.get(asset.type) ?? asset.type;
    }

    const parentCollection = path[path.length - 2];
    return ObjectTypesMap.get(parentCollection) ?? parentCollection;
  }

  private static async mutate<T extends AssetMutation>(
    asset: Asset,
    mutateParams: MutateParams<T>,
    requestId = uuidv4(),
    waitForResponse = false,
  ): Promise<Asset> {
    const { path, ...mutationWithoutRef } = mutateParams;
    const ref = this.getRef(['assets', asset.id, ...path]);
    const mutation = { ...mutationWithoutRef, ref } as AssetMutation;

    applyMutation(asset, mutation);

    const clientMessage: ClientMessage = {
      type: 'DoMutationClientMessage',
      request_id: requestId,
      mutation,
    };

    if (waitForResponse) {
      await useWebSocketStore
        .getState()
        .sendMessageAndWaitForResponse(
          clientMessage,
          (response) =>
            response.type === 'NotifyAboutAssetMutationServerMessage' &&
            response.request_id === requestId &&
            response.mutation.ref.id === mutation.ref.id &&
            response.mutation.type === mutation.type,
        );
    } else {
      await useWebSocketStore.getState().sendMessage(clientMessage);
    }

    return asset;
  }

  static async delete({ asset, path, requestId, waitForResponse }: DeleteParams): Promise<Asset> {
    return this.mutate<DeleteMutation>(asset, { path, type: 'DeleteMutation' }, requestId, waitForResponse);
  }

  static async update({ asset, path = [], key, value, requestId, waitForResponse }: UpdateParams): Promise<Asset> {
    return this.mutate<SetValueMutation>(
      asset,
      { path, type: 'SetValueMutation', key, value },
      requestId,
      waitForResponse,
    );
  }

  static async create({ asset, path = [], object, requestId, waitForResponse }: CreateParams): Promise<Asset> {
    const asset_ = asset ?? (object as Asset);

    const object_type = this.getObjectType(asset_, path);
    return this.mutate<CreateMutation>(
      asset_,
      { path, type: 'CreateMutation', object, object_type },
      requestId,
      waitForResponse,
    );
  }

  static async append({ asset, path, key, value, requestId, waitForResponse }: AppendParams): Promise<Asset> {
    return this.mutate<AppendToStringMutation>(
      asset,
      { path, type: 'AppendToStringMutation', key, value },
      requestId,
      waitForResponse,
    );
  }
}

type WithoutRef<T> = Omit<T, 'ref'>;
type WithPathInsteadOfRef<T> = WithoutRef<T> & {
  path: string[];
};

type MutateParams<T extends AssetMutation> = T extends CreateMutation
  ? WithPathInsteadOfRef<CreateMutation>
  : T extends DeleteMutation
  ? WithPathInsteadOfRef<DeleteMutation>
  : T extends SetValueMutation
  ? WithPathInsteadOfRef<SetValueMutation>
  : T extends AppendToStringMutation
  ? WithPathInsteadOfRef<AppendToStringMutation>
  : never;

type BaseParams = {
  asset: Asset;
  path: string[];
  requestId?: string;
  waitForResponse?: boolean;
};

type AppendParams = BaseParams & {
  key: string;
  value: string;
};

type CreateParams = Omit<BaseParams, 'path' | 'asset'> & {
  path?: string[];
  asset?: Asset;
  object: Record<string, any>;
};

type DeleteParams = BaseParams;

type UpdateParams = Omit<BaseParams, 'path'> & {
  path?: string[];
  key: string;
  value: any;
};
