// The AIConsole Project
//
// Copyright 2023 10Clouds
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import * as ReactAlertDialog from '@radix-ui/react-alert-dialog';
import { Button } from './Button';
import { useEffect, useState } from 'react';

interface AlertDialogProps {
  title: string;
  confirmationButtonText?: string;
  cancelButtonText?: string;
  isOpen?: boolean;
  openModalButton?: React.ReactElement;
  onClose?: () => void;
  onConfirm?: () => void;
  children?: React.ReactNode;
}

const AlertDialog: React.FC<AlertDialogProps> = ({
  title,
  confirmationButtonText = 'Save',
  cancelButtonText = 'Close',
  isOpen = false,
  openModalButton,
  children,
  onClose,
  onConfirm,
}) => {
  const [open, setOpen] = useState(isOpen);
  const onBackgroundClick = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    // Close modal if the background is clicked directly
    if (e.target === e.currentTarget) {
      onClose?.();
    }
  };

  useEffect(() => {
    setOpen(isOpen);
  }, [isOpen]);

  const handleClose = () => {
    setOpen(false);
    onClose?.();
  };

  return (
    <ReactAlertDialog.Root open={open} onOpenChange={setOpen}>
      {openModalButton && <ReactAlertDialog.Trigger asChild>{openModalButton}</ReactAlertDialog.Trigger>}
      <ReactAlertDialog.Portal>
        <ReactAlertDialog.Overlay
          className="data-[state=open]:animate-overlayShow fixed inset-0 bg-black/50 z-[98]"
          onClick={onBackgroundClick}
        />
        <ReactAlertDialog.Content
          className="p-10 flex flex-col gap-[30px] text-center text-white data-[state=open]:animate-contentShow fixed top-[50%] left-[50%] max-h-[85vh] max-w-[380px] translate-x-[-50%] translate-y-[-50%] rounded-xl bg-primary-gradient shadow-dark focus:outline-none z-[99]"
          onEscapeKeyDown={handleClose}
          onOpenAutoFocus={(e) => e.preventDefault()}
        >
          <div className="flex flex-col gap-[10px]">
            <ReactAlertDialog.Title className="text-white text-[22px] font-black">{title}</ReactAlertDialog.Title>
            {children && (
              <ReactAlertDialog.Description className="font-normal text-sm text-center text-gray-300 whitespace-pre-line">
                {children}
              </ReactAlertDialog.Description>
            )}
          </div>
          <div className="flex w-full gap-[10px] justify-center">
            <Button variant="secondary" bold small onClick={handleClose}>
              {cancelButtonText}
            </Button>
            <Button variant="primary" small onClick={onConfirm} autoFocus>
              {confirmationButtonText}
            </Button>
          </div>
        </ReactAlertDialog.Content>
      </ReactAlertDialog.Portal>
    </ReactAlertDialog.Root>
  );
};

export default AlertDialog;
