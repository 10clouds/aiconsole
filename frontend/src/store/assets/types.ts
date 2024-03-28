import { DataContext } from './DataContext';
import { Asset } from './constructors';

interface TBaseObject {
  id: string;
  lock_id?: string | null;
}

export class BaseObject implements TBaseObject {
  constructor(
    public id: string,
    public lock_id: string | null = null,
  ) {}
}

interface TCollectionRef extends TBaseObject {
  parent: TObjectRef | null;
  context: DataContext | null;
}

interface TObjectRef extends TBaseObject {
  parent_collection: TCollectionRef;
  context: DataContext | null;
}

type TCollectionRefWithoutContext = Omit<TCollectionRef, 'context' | 'parent'> & {
  parent: TObjectRefWithoutContext | null;
};
type TObjectRefWithoutContext = Omit<TObjectRef, 'context' | 'parent_collection'> & {
  parent_collection: TCollectionRefWithoutContext;
};

interface TAttributeRef {
  name: string;
  object: TObjectRef;
  context: DataContext | null;
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
    public parent: ObjectRef | null = null,
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
        ref: new ObjectRef<T>(object.id, this, this.context),
        object,
        object_type: object.constructor.name,
      });
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  getById(id: string) {
    return new ObjectRef(id, this, this.context);
  }

  get sendable(): TCollectionRefWithoutContext {
    return {
      id: this.id,
      parent: this.parent ? this.parent.sendable : null,
    };
  }
}

export class ObjectRef<T extends BaseObject = BaseObject> extends BaseObject implements TObjectRef {
  constructor(
    id: string,
    public parent_collection: CollectionRef<T | BaseObject>,
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

  static fromObject(obj: ObjectRef, context: DataContext | null = null): ObjectRef {
    if (!obj.id) {
      throw new Error("Object must have an 'id' property to create an ObjectRef.");
    }
    const parentCollection = new CollectionRef(
      obj.parent_collection.id,
      obj.parent_collection.parent ? ObjectRef.fromObject(obj.parent_collection.parent, context) : null,
      context,
    );
    return new ObjectRef(obj.id, parentCollection, context);
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
      return this.context.get(this) as T;
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  exists(): boolean {
    if (this.context !== null) {
      return this.context.exists(this);
    }
    throw new Error('Context must be set externally after deserialisation to use the object.');
  }

  get sendable(): TObjectRefWithoutContext {
    return {
      id: this.id,
      parent_collection: this.parent_collection.sendable,
    };
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
