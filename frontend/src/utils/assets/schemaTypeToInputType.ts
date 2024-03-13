export function schemaTypeToInputType(schemaType: string): string {
  const typeMapping: { [key: string]: string } = {
    integer: 'number',
    float: 'number',
    number: 'number',
    string: 'text',
    boolean: 'checkbox',
  };

  return typeMapping[schemaType] || 'text';
}
