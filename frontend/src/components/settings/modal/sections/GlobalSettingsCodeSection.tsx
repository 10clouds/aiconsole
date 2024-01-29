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

import type { Control } from 'react-hook-form';
import { useWatch } from 'react-hook-form';
import { Ban, Check } from 'lucide-react';

import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
import { GlobalSettingsFormData } from '@/forms/globalSettingsForm';

interface GlobalSettingsCodeSectionProps {
  control: Control<GlobalSettingsFormData>;
  onChange: (autorun: boolean) => void;
}

const GlobalSettingsCodeSection = ({ control, onChange }: GlobalSettingsCodeSectionProps) => {
  const watchAutorun = useWatch({ control, name: 'code_autorun' });

  return (
    <div className="border border-gray-600 rounded-xl py-[15px] px-5 flex flex-col gap-4">
      <div className="flex items-center gap-5">
        <h4 className="text-white text-[15px] leading-[19px]">Always run code</h4>
        <div className="flex items-center gap-[10px]">
          <Button statusColor={watchAutorun ? 'green' : 'base'} variant="status" onClick={() => onChange(true)}>
            <Icon icon={Check} /> YES
          </Button>
          <Button statusColor={!watchAutorun ? 'red' : 'base'} variant="status" onClick={() => onChange(false)}>
            <Icon icon={Ban} /> NO
          </Button>
        </div>
      </div>
      <span className="text-xs text-gray-400 block">
        The agents can automatically run code they produce in the chat. Select "Yes" if you want to enable it or "No"
        if you want to approve the code manually.
      </span>
    </div>
  );
};
export default GlobalSettingsCodeSection;
