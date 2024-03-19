import { upperFirst } from '@mantine/hooks';

export const updateDocumentTitle = (title: string) => {
  const isWebBrowser = window.electron === undefined;

  if (isWebBrowser) document.title = upperFirst(title);
};
