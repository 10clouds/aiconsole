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

import { Button } from '@/components/common/Button';
import { Icon } from '@/components/common/icons/Icon';
import { Ban, Check } from 'lucide-react';

interface GlobalSettingsCodeSectionProps {
  isAutoRun: boolean;
  setIsAutoRun: (value: boolean) => void;
}

const GlobalSettingsCodeSection = ({ isAutoRun, setIsAutoRun }: GlobalSettingsCodeSectionProps) => {
  return (
    <div className="border border-gray-600 rounded-xl p-[20px] pt-[15px] flex flex-col gap-5">
      <p className="text-white text-[15px] leading-6">Code run</p>
      <div className="flex items-center gap-5">
        <h4 className="text-white font-semibold text-[16px] leading-[19px]">Always run code</h4>
        <div className="flex items-center gap-[10px]">
          <Button statusColor={isAutoRun ? 'green' : 'base'} variant="status" onClick={() => setIsAutoRun(true)}>
            <Icon icon={Check} /> YES
          </Button>
          <Button statusColor={!isAutoRun ? 'red' : 'base'} variant="status" onClick={() => setIsAutoRun(false)}>
            <Icon icon={Ban} /> NO
          </Button>
        </div>
      </div>
    </div>
  );
};
export default GlobalSettingsCodeSection;
