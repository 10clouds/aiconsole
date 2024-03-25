import { ObjectRef } from '@/types/assets/assetTypes';

export const getRef = (path: string[]): ObjectRef => {
  return {
    id: path[0],
    parent_collection: {
      id: path[1],
      parent: path.length > 2 ? getRef(path.slice(2)) : null,
    },
  };
};
