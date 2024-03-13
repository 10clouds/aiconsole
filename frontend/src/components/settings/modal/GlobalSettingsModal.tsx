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
import { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { Content, Portal, Root } from '@radix-ui/react-dialog';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import TopGradient from '@/components/common/TopGradient';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { Button } from '../../common/Button';
import { Icon } from '../../common/icons/Icon';
import GlobalSettingsApiSection from './sections/GlobalSettingsApiSection';
import GlobalSettingsCodeSection from './sections/GlobalSettingsCodeSection';
import GlobalSettingsUserSection from './sections/GlobalSettingsUserSection';
import { GlobalSettingsFormData, GlobalSettingsFormSchema } from '@/forms/globalSettingsForm';
import { UnsavedSettingsDialog } from '@/components/common/UnsavedSettingsDialog';
import { PartialSettingsData } from '@/types/settings/settingsTypes';

// TODO: implement other features from figma like api for azure, user profile and tutorial
export const GlobalSettingsModal = () => {
  const isSettingsModalVisible = useSettingsStore((state) => state.isSettingsModalVisible);
  const setSettingsModalVisibility = useSettingsStore((state) => state.setSettingsModalVisibility);

  const display_name = useSettingsStore((state) => state.settings.user_profile?.display_name);
  const profilePicture = useSettingsStore((state) => state.settings.user_profile?.profile_picture);
  const openAiApiKey = useSettingsStore((state) => state.settings.openai_api_key);
  const codeAutorun = useSettingsStore((state) => state.settings.code_autorun);
  const saveSettings = useSettingsStore((state) => state.saveSettings);

  const [confirmationDialogOpen, setConfirmationDialogOpen] = useState(false);

  const { reset, control, setValue, formState, handleSubmit } = useForm<GlobalSettingsFormData>({
    resolver: zodResolver(GlobalSettingsFormSchema),
  });

  useEffect(() => {
    // Initial form values are cached, so we need to reset with the right ones
    if (isSettingsModalVisible) {
      reset({
        user_profile: {
          display_name: display_name,
          avatarBase64: profilePicture,
        },
        openai_api_key: openAiApiKey,
        code_autorun: codeAutorun,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSettingsModalVisible]);

  const onSubmit = (data: GlobalSettingsFormData) => {
    // No fields changed, close the modal
    if (!Object.keys(formState.dirtyFields).length) {
      setSettingsModalVisibility(false);
      return;
    }

    // Fields we don't want to directly send
    const ignoreFields = ['avatar'];

    let avatarFormData: FormData | null = null;

    // Get all modified fields from the form state
    const dirtyFields = Object.keys(formState.dirtyFields) as Array<keyof GlobalSettingsFormData>;

    // Create FormData if there's an avatar file selected
    if (dirtyFields.includes('avatar') && data.avatar) {
      avatarFormData = new FormData();
      avatarFormData.append('avatar', data.avatar);
    }

    // Filter out ignored fields and create the data object
    const profileData = dirtyFields
      .filter((field) => !ignoreFields.includes(field))
      .reduce<PartialSettingsData>((prev, next) => {
        return { ...prev, [next]: data[next] };
      }, {});

    saveSettings(profileData, true, avatarFormData);

    setSettingsModalVisibility(false);
  };

  const handleSetAvatarImage = (avatar: File) => setValue('avatar', avatar, { shouldDirty: true });

  const handleSetAutorun = (autorun: boolean) => setValue('code_autorun', autorun, { shouldDirty: true });

  const handleModalClose = () => {
    if (Object.keys(formState.dirtyFields).length) {
      setConfirmationDialogOpen(true);
      return;
    }
    setSettingsModalVisibility(false);
  };

  const discardChanges = () => {
    setConfirmationDialogOpen(false);
    setSettingsModalVisibility(false);
  };

  const hideConfirmationDialog = () => setConfirmationDialogOpen(false);

  return (
    <Root open={isSettingsModalVisible}>
      <Portal>
        <Content asChild className="fixed" onEscapeKeyDown={handleModalClose}>
          <div className="w-full h-[100vh] z-[98] top-0 left-0 right-0 bg-gray-900">
            <TopGradient />
            <div className="flex justify-between items-center px-[20px] py-[7px] relative z-10 border-gray-600 border-b h-[80px] min-h-[80px]">
              <img src="favicon.png" className="shadows-lg h-[36px] w-[36px]" alt="Logo" />
              <h3 className="text-gray-400 text-[15px] leading-[24px]">AIConsole settings</h3>
              <Button variant="secondary" onClick={handleModalClose} small>
                <Icon icon={X} />
                Close
              </Button>
            </div>
            <div className="h-[calc(100%-100px)] max-w-[720px] mx-auto relative flex flex-col justify-self-start gap-5 overflow-y-auto px-5 pt-3 mt-3">
              <form onSubmit={handleSubmit(onSubmit)}>
                <GlobalSettingsUserSection
                  control={control}
                  avatarBase64={profilePicture}
                  onImageSelected={handleSetAvatarImage}
                />
                <GlobalSettingsApiSection control={control} />
                <GlobalSettingsCodeSection control={control} onChange={handleSetAutorun} />
                <div className="flex items-center justify-end gap-[10px] mt-[30px] mb-6">
                  <Button variant="secondary" bold onClick={handleModalClose}>
                    Cancel
                  </Button>
                  <Button type="submit">{'Save'}</Button>
                </div>
              </form>
            </div>
            <UnsavedSettingsDialog
              onCancel={hideConfirmationDialog}
              isOpen={confirmationDialogOpen}
              onConfirm={discardChanges}
            />
          </div>
        </Content>
      </Portal>
    </Root>
  );
};
