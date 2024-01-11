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

import { ToastMessage, ToastVariant, useToastsStore } from '@/store/common/useToastsStore';
import * as ReactToast from '@radix-ui/react-toast';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';
import { ElementRef, ReactNode, forwardRef } from 'react';
import { Icon } from './icons/Icon';

export function ToastProvider({ children }: { children: ReactNode }) {
  const toasts = useToastsStore((state) => state.toasts);
  const removeToast = useToastsStore((state) => state.removeToast);

  const onToastClose = (toastId: string) => {
    removeToast(toastId);
  };

  return (
    <ReactToast.Provider>
      {children}
      <AnimatePresence mode="popLayout">
        {toasts.map(({ id, title, message, variant }) => {
          return <Toast key={id} title={title} message={message} variant={variant} onClose={() => onToastClose(id)} />;
        })}
      </AnimatePresence>

      <ReactToast.Viewport className="max-sm:top-20 fixed top-4 right-4 flex flex-col-reverse gap-3 z-50" />
    </ReactToast.Provider>
  );
}

const getStyles = (variant: ToastVariant) => {
  switch (variant) {
    case 'success':
      return 'border-green';
    case 'error':
      return 'border-red';
    case 'info':
      return 'border-gray-400';
  }
};

type ToastProps = ToastMessage & {
  onClose: () => void;
};

const Toast = forwardRef<ElementRef<typeof ReactToast.Root>, ToastProps>(
  ({ title, message, variant = 'info', onClose }, forwardedRef) => {
    const WIDTH = 400;
    const MARGIN = 16;

    return (
      <ReactToast.Root
        ref={forwardedRef}
        asChild
        forceMount
        duration={2000}
        onOpenChange={onClose}
        className="rounded-md shadow-dark w-full items-center"
      >
        <motion.li
          layout
          initial={{ x: WIDTH + MARGIN }}
          animate={{ x: 0 }}
          exit={{
            opacity: 0,
            x: WIDTH + MARGIN,
            zIndex: -1,
            transition: {
              opacity: { duration: 0.1 },
            },
          }}
          transition={{
            type: 'spring',
            mass: 1,
            damping: 30,
            stiffness: 200,
            duration: 0.1,
          }}
          style={{ width: WIDTH, WebkitTapHighlightColor: 'transparent' }}
          className="py-5 px-[15px] rounded-lg shadow-md bg-gray-700 text-white text-sm"
        >
          <div className="flex items-start justify-between bg-gray-700 text-sm text-white shadow-sm backdrop-blur">
            <div
              className={`flex flex-col items-start pl-5 border-l-[3px] w-full overflow-hidden ${getStyles(variant)}`}
            >
              <ReactToast.Title className="font-semibold text-base w-full truncate">{title}</ReactToast.Title>
              <ReactToast.Description className="text-[15px] w-full leading-6 text-gray-300 text-balance">
                {message}
              </ReactToast.Description>
            </div>
            <ReactToast.Close className=" text-gray-300 transition hover:text-gray-200 w-5 h-5">
              <Icon icon={X} width={16} height={16} className="w-4 h-4" />
            </ReactToast.Close>
          </div>
        </motion.li>
      </ReactToast.Root>
    );
  },
);
