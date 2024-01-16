import { ReactNode } from 'react';
import * as Dialog from '@radix-ui/react-dialog';

interface CodeInputFullScreenProps {
  children: ReactNode;
  open: boolean;
  setOpen: (open: boolean) => void;
}

export const CodeInputFullScreen = ({ children, setOpen, open }: CodeInputFullScreenProps) => {
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="bg-black/70 h-[100vh] w-full flex items-center justify-center relative z-[100]">
          <Dialog.Content className="w-[85%]">{children}</Dialog.Content>
        </Dialog.Overlay>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
