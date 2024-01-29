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

import Tooltip from '@/components/common/Tooltip';
import { cn } from '@/utils/common/cn';
import { ChangeEvent, ReactNode, forwardRef } from 'react';
import TextareaAutosize from 'react-textarea-autosize';
import { HelperLabel } from './HelperLabel';

const REQUIRED_ERROR_MESSAGE = 'This field is required.';

export type ErrorObject = {
  [key: string]: string | null;
};

export const checkErrors = (errors: ErrorObject): boolean => {
  for (const key in errors) {
    if (errors[key as keyof ErrorObject]) {
      return true;
    }
  }
  return false;
};

interface TextInputProps {
  label?: string;
  value?: string;
  name: string;
  className?: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  errors?: ErrorObject;
  error?: string;
  setErrors?: React.Dispatch<React.SetStateAction<ErrorObject>>;
  withTooltip?: boolean;
  tootltipText?: string;
  horizontal?: boolean;
  fullWidth?: boolean;
  resize?: boolean;
  helperText?: string;
  learnMoreLink?: string;
  labelChildren?: ReactNode;
  hidden?: boolean;
  type?: HTMLInputElement['type'];
}

export const TextInput = forwardRef<HTMLElement, TextInputProps>(
  (
    {
      label,
      value,
      className,
      onChange,
      onBlur,
      placeholder,
      disabled = false,
      required,
      name,
      error,
      setErrors,
      withTooltip = false,
      horizontal,
      tootltipText,
      fullWidth,
      resize,
      helperText,
      learnMoreLink,
      labelChildren,
      hidden,
      type,
    },
    ref,
  ) => {
    const checkIfEmpty = (value: string) => {
      if (required && value.trim() === '') {
        setErrors?.((prevErrors) => ({
          ...prevErrors,
          ...{ [name]: REQUIRED_ERROR_MESSAGE },
        }));
      } else {
        setErrors?.((prevErrors) => ({
          ...prevErrors,
          ...{ [name]: null },
        }));
      }
    };

    const handleBlur = (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
      onBlur?.();
      checkIfEmpty(e.target.value);
    };

    const handleChange = (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
      onChange(e.target.value);
      checkIfEmpty(e.target.value);
    };

    const textFieldProps = {
      className: cn(
        className,
        'max-h-[120px] w-full overflow-y-auto border border-gray-500 placeholder:text-gray-400',
        'bg-gray-800 text-[15px] text-gray-300 focus:text-white flex-grow resize-none rounded-[8px]',
        'px-[20px] py-[12px] hover:bg-gray-600 hover:placeholder:text-gray-300 focus:bg-gray-600',
        'focus:border-gray-400 focus:outline-none transition duration-100',
        { 'border-danger': error },
      ),
      value,
      id: label,
      onChange: handleChange,
      disabled,
      onBlur: handleBlur,
      placeholder,
      type,
    };

    const textarea = <TextareaAutosize ref={ref as React.Ref<HTMLTextAreaElement>} {...textFieldProps} rows={1} />;

    const input = <input ref={ref as React.Ref<HTMLInputElement>} {...textFieldProps} />;

    const core = resize ? textarea : input;

    return (
      <>
        <div
          className={cn('flex gap-[20px] flex-col relative', {
            'flex-row items-center': horizontal,
            'w-full': fullWidth,
          })}
        >
          {label ? (
            <div className="text-white text-[15px] flex items-center gap-[30px] ">
              <label htmlFor={label} className="min-w-max">
                {label}
              </label>
              {labelChildren}
              {helperText ? <HelperLabel helperText={helperText} learnMoreLink={learnMoreLink} /> : null}
            </div>
          ) : null}

          {withTooltip && !hidden ? (
            <Tooltip label={tootltipText} position="top" align="end" disableAnimation>
              {core}
            </Tooltip>
          ) : null}

          {!withTooltip && !hidden ? core : null}
          {error && !hidden && (
            <div className="text-danger flex justify-end text-xs absolute right-0 -bottom-[20px]">{error}</div>
          )}
        </div>
      </>
    );
  },
);
