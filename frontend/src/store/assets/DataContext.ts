import { AssetMutation } from '@/api/ws/assetMutations';
import { BaseObject, CollectionRef, ObjectRef, Root } from './types';
import { applyMutation } from '@/api/ws/chat/applyMutation';
import { useWebSocketStore } from '@/api/ws/useWebSocketStore';
import { v4 as uuidv4 } from 'uuid';
import { Asset } from './constructors';
import { useAssetStore } from './useAssetStore';

interface TDataContext {
  mutate<T extends BaseObject>(mutation: AssetMutation<T>): Promise<void>;
  get<T extends ObjectRef | CollectionRef>(ref: T): BaseObject | BaseObject[] | null;
  exists(ref: ObjectRef<any> | CollectionRef<any>): boolean;
}

type AssetKeyWithBaseObjectArray = {
  [K in keyof Asset]: Asset[K] extends BaseObject[] ? K : never;
}[keyof Asset];

export class DataContext implements TDataContext {
  async mutate<T extends BaseObject>(mutation: AssetMutation<T>): Promise<void> {
    applyMutation(this, mutation);
    useWebSocketStore.getState().sendMessage({
      type: 'DoMutationClientMessage',
      mutation: {
        ...mutation,
        ref: mutation.ref.sendable,
      },
      request_id: uuidv4(),
    });
  }

  get<T extends ObjectRef | CollectionRef>(ref: T): BaseObject | BaseObject[] | null {
    let obj: BaseObject | Asset | null = new Root();
    const segments = ref.ref_segments;
    if (!segments.length) {
      return obj;
    }

    let segment = segments.shift() as string;
    if (segment === 'assets') {
      if (!segments.length) {
        return useAssetStore.getState().assets;
      }
      // Get the object from the assets collection
      segment = segments.shift() as string;
      obj = useAssetStore.getState().getAsset(segment) ?? null;

      if (!obj || !segments.length) {
        return obj as BaseObject | null;
      }

      while (segments.length) {
        // Get the sub collection
        segment = segments.shift() as string;
        const col: BaseObject[] | null = (obj as Asset)[segment as AssetKeyWithBaseObjectArray];

        if (!col || !segments.length) {
          return col;
        }

        // Get the object from the sub collection
        segment = segments.shift() as string;
        obj = (col as BaseObject[]).find((x) => x.id === segment) ?? null;

        if (!obj || !segments.length) {
          return obj;
        }
      }
    }
    throw new Error(`Unknown ref type ${ref}`);
  }

  exists(ref: ObjectRef | CollectionRef): boolean {
    return this.get(ref) !== null;
  }

  acquireLock(ref: ObjectRef): string | null {
    const obj = this.get(ref) as BaseObject;
    let lockId = null;

    if (obj !== null && obj.lock_id === null) {
      lockId = uuidv4();
      obj.lock_id = lockId;
    }

    return lockId;
  }

  realeaseLock(ref: ObjectRef) {
    const obj = this.get(ref) as BaseObject;

    if (obj !== null && obj.lock_id !== null) {
      obj.lock_id = null;
    }
  }
}
