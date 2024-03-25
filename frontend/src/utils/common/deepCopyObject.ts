export const deepCopyObject = <T extends Record<string, any>>(obj: T): T => {
  const newObj = { ...obj };
  for (const key in newObj) {
    if (typeof newObj[key] === 'object') {
      newObj[key] = deepCopyObject(newObj[key]);
    } else if (Array.isArray(obj[key])) {
      newObj[key] = newObj[key].map((item: any) => {
        if (typeof item === 'object') {
          return deepCopyObject(item);
        }
        return item;
      });
    }
  }

  return newObj;
};
