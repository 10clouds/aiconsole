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
import { useState } from 'react';
import { Controller, useWatch } from 'react-hook-form';
import type { Control } from 'react-hook-form';
import { Pencil } from 'lucide-react';

import ImageUploader from '@/components/common/ImageUploader';
import { Icon } from '@/components/common/icons/Icon';
import { TextInput } from '@/components/assets/TextInput';
import { GlobalSettingsFormData } from '@/forms/globalSettingsForm';

interface GlobalSettingsUserSectionProps {
  control: Control<GlobalSettingsFormData>;
  onImageSelected: (avatar: File) => void;
  avatarBase64?: string;
}

const GlobalSettingsUserSection = ({ onImageSelected, avatarBase64, control }: GlobalSettingsUserSectionProps) => {
  const [isEditMode, setIsEditMode] = useState(false);

  const watchName = useWatch({ control, name: 'user_profile.display_name' });

  const handleNameInputBlur = () => setIsEditMode(false);

  return (
    <div className="flex items-stretch w-full gap-[30px] bg-secondary-gradient p-5 rounded-xl mb-5 border-gray-600 border">
      <ImageUploader
        currentImage={avatarBase64}
        onUpload={(avatar) => onImageSelected(new File([avatar], 'avatar'))}
      />
      <div className="flex flex-col justify-between">
        <div className="flex gap-2.5 flex-col">
          <span className="text-white text-[15px]">User name</span>
          {isEditMode ? (
            <Controller
              name="user_profile.display_name"
              control={control}
              render={({ field }) => (
                <TextInput
                  type="text"
                  placeholder="Your name"
                  {...field}
                  onBlur={handleNameInputBlur}
                  ref={(e) => {
                    field.ref(e);
                    e?.focus();
                  }}
                />
              )}
            />
          ) : (
            <div className="flex gap-5 items-center">
              <h2 className="text-white text-[32px] font-extrabold truncate max-w-[30dvw] md:max-w-sm">
                {watchName || 'Your name'}
              </h2>
              <button onClick={() => setIsEditMode(true)}>
                <Icon icon={Pencil} className="text-gray-400 h-6 w-6" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default GlobalSettingsUserSection;
