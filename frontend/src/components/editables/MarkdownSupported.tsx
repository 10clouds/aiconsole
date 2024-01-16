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

import { cn } from '@/utils/common/cn';

import { MarkdownLogoIcon } from '../common/icons/MarkdownLogo';

interface MarkdownSupportedProps {
  className?: string;
}

export const MarkdownSupported = ({ className }: MarkdownSupportedProps) => (
  <div className="flex justify-end pr-2 pt-2">
    <a
      target="_blank"
      href="https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax"
      className={cn('hover:text-yellow text-sm flex items-center', className)}
    >
      <MarkdownLogoIcon className="mr-1" /> Markdown is supported
    </a>
  </div>
);
