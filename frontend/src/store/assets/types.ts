import { AssetMutation } from '@/api/ws/assetMutations';
import { useAssetStore } from './useAssetStore';
import { Asset } from '@/types/assets/assetTypes';
import { applyMutation } from '@/api/ws/chat/applyMutation';
import { v4 as uuidv4 } from 'uuid';

interface TBaseObject {
  id: string;
  lock_id?: string | null;
}

type AssetKeyWithBaseObjectArray = {
  [K in keyof Asset]: Asset[K] extends BaseObject[] ? K : never;
}[keyof Asset];

interface TDataContext {
  mutate<T extends BaseObject>(mutation: AssetMutation<T>): Promise<void>;
  get<T extends ObjectRef | CollectionRef>(ref: T): BaseObject | BaseObject[] | null;
  exists(ref: ObjectRef<any> | CollectionRef<any>): boolean;
}

export class DataContext implements TDataContext {
  async mutate<T extends BaseObject>(mutation: AssetMutation<T>): Promise<void> {
    applyMutation(this, mutation);
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
        return useAssetStore.getState().subscribedAssets;
      }
      // Get the object from the assets collection
      segment = segments.shift() as string;
      obj = useAssetStore.getState().getSubscribedAsset(segment) ?? null;

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

  acquireLock(ref: ObjectRef<any>): string | null {
    const obj = this.get(ref);
    let lockId = null;

    if (obj !== null && obj.lock_id === null) {
      lockId = uuidv4();
      obj.lock_id = lockId;
    }

    return lockId;
  }

  realeaseLock(ref: ObjectRef<any>) {
    const obj = this.get(ref);

    if (obj !== null && obj.lock_id !== null) {
      obj.lock_id = null;
    }
  }
}

interface TCollectionRef extends TBaseObject {
  parent: TObjectRef | null;
  context: DataContext | null;
}

interface TObjectRef extends TBaseObject {
  parent_collection: TCollectionRef;
  context: DataContext | null;
}

interface TAttributeRef {
  name: string;
  object: TObjectRef;
  context: DataContext | null;
}

export class BaseObject implements TBaseObject {
  constructor(
    public id: string,
    public lock_id: string | null = null,
  ) {}
}

export class Root extends BaseObject {
  assets: Asset[];

  constructor() {
    super('root');
    this.assets = [];
  }
}

export class CollectionRef<T extends BaseObject = BaseObject> extends BaseObject implements TCollectionRef {
  constructor(
    id: string,
    public parent: ObjectRef<T> | null = null,
    public context: DataContext | null = null,
  ) {
    super(id);
  }

  get ref_segments(): string[] {
    let ref: TCollectionRef | null = this;
    const segments: string[] = [];
    while (ref !== null) {
      segments.push(ref.id);
      if (ref.parent !== null) {
        segments.push(ref.parent.id);
        ref = ref.parent.parent_collection;
      } else {
        ref = null;
      }
    }
    return segments.reverse();
  }

  get(): T[] {
    if (this.context !== null) {
      return this.context.get(this) as T[];
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  async create<T extends BaseObject>(object: T) {
    if (this.context !== null) {
      return await this.context.mutate({
        type: 'CreateMutation',
        ref: new ObjectRef(object.id, this, this.context),
        object,
        object_type: object.constructor.name,
      });
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  getById(id: string) {
    return new ObjectRef(id, this);
  }
}

export class ObjectRef<T extends BaseObject = BaseObject> extends BaseObject implements TObjectRef {
  constructor(
    id: string,
    public parent_collection: CollectionRef<T>,
    public context: DataContext | null = null,
  ) {
    super(id);
  }

  get ref_segments(): string[] {
    let ref: TObjectRef | null = this;
    const segments = [];
    while (ref && ref !== null) {
      segments.push(ref.id);
      segments.push(ref.parent_collection.id);
      ref = ref.parent_collection.parent;
    }
    return segments.reverse();
  }

  collection(id: string): TCollectionRef {
    if (this.context !== null) {
      return new CollectionRef(id, this, this.context);
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  async set(key: string, value: any) {
    if (this.context !== null) {
      return await this.context.mutate({
        type: 'SetValueMutation',
        ref: this,
        key,
        value,
      });
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  async delete() {
    if (this.context !== null) {
      return await this.context.mutate({ type: 'DeleteMutation', ref: this });
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  get(): T {
    if (this.context !== null) {
      return this.context.get<T>(this) as T;
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  exists(): boolean {
    if (this.context !== null) {
      return this.context.exists(this);
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }
}

export class AttributeRef<T> implements TAttributeRef {
  constructor(
    public name: string,
    public object: ObjectRef,
    public context: DataContext | null = null,
  ) {}

  async set(value: T) {
    if (this.context !== null) {
      return await this.context.mutate({
        type: 'SetValueMutation',
        ref: this.object,
        key: this.name,
        value,
      });
    }
  }

  get() {
    if (this.context === null) return null;

    const obj = this.context.get(this.object) as BaseObject;
    return obj[this.name as keyof BaseObject] as T;
  }
}

export class StringAttributeRef extends AttributeRef<string> {
  set(value: string) {
    return super.set(value);
  }

  async append(value: string) {
    if (this.context !== null) {
      return this.context.mutate({
        type: 'AppendToStringMutation',
        ref: this.object,
        key: this.name,
        value,
      });
    }
  }

  get() {
    return super.get();
  }
}
