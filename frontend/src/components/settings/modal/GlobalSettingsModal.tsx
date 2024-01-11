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

import TopGradient from '@/components/common/TopGradient';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useApiKey } from '@/utils/settings/useApiKey';
import { useDisclosure } from '@mantine/hooks';
import { Content, Portal, Root } from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from '../../common/Button';
import { Icon } from '../../common/icons/Icon';
import GlobalSettingsApiSection from './sections/GlobalSettingsApiSection';
import GlobalSettingsCodeSection from './sections/GlobalSettingsCodeSection';
import GlobalSettingsUserSection from './sections/GlobalSettingsUserSection';

// TODO: implement other features from figma like api for azure, user profile and tutorial
export const GlobalSettingsModal = () => {
  const { username, userEmail: email, openAiApiKey, alwaysExecuteCode, saveSettings } = useSettingsStore();
  const isSettingsModalVisible = useSettingsStore((state) => state.isSettingsModalVisible);
  const setSettingsModalVisibility = useSettingsStore((state) => state.setSettingsModalVisibility);

  const [usernameFormValue, setUsernameFormValue] = useState(username || '');
  const [emailFormValue, setEmailFormValue] = useState(email || '');
  const [apiKeyValue, setApiKeyValue] = useState(openAiApiKey || '');
  const [isAutoRun, setIsAutoRun] = useState(alwaysExecuteCode);
  const [userAvatarData, setUserAvatarData] = useState<File>();
  const [isAvatarOverwritten, setIsAvatarOverwritten] = useState(false);

  const { validating, setApiKey } = useApiKey();

  useEffect(() => {
    if (isSettingsModalVisible) {
      setUsernameFormValue(username || '');
      setEmailFormValue(email || '');
    }
  }, [isSettingsModalVisible, username, email]);

  useEffect(() => {
    if (isAutoRun !== alwaysExecuteCode) {
      setIsAutoRun(alwaysExecuteCode);
    }
  }, [alwaysExecuteCode]);

  const handleOpen = () => {
    if (openAiApiKey) {
      setApiKeyValue(openAiApiKey);
    }
  };

  const onClose = () => {
    setSettingsModalVisibility(false);
  };

  const [opened, { close, open }] = useDisclosure(isSettingsModalVisible, { onClose, onOpen: handleOpen });

  useEffect(() => {
    if (isSettingsModalVisible) {
      open();
    } else {
      close();
    }
  }, [close, isSettingsModalVisible, open]);

  const save = async () => {
    if (apiKeyValue !== openAiApiKey) {
      await setApiKey(apiKeyValue);
    }

    let avatarFormData: FormData | null = null;

    // check if avatar was overwritten to avoid sending unnecessary requests
    if (isAvatarOverwritten && userAvatarData) {
      avatarFormData = new FormData();
      avatarFormData.append('avatar', userAvatarData);
    }

    saveSettings(
      {
        username: usernameFormValue !== username ? usernameFormValue : undefined,
        email: emailFormValue !== email ? emailFormValue : undefined,
        openai_api_key: apiKeyValue !== openAiApiKey ? apiKeyValue : undefined,
        code_autorun: isAutoRun !== alwaysExecuteCode ? isAutoRun : undefined,
      },
      true,
      avatarFormData,
    );
    resetFormFields();
    close();
  };

  const resetFormFields = () => {
    setUsernameFormValue('');
    setEmailFormValue('');
    setApiKeyValue('');
    setIsAvatarOverwritten(false);
  };

  const handleSetAvatarImage = (avatar: File) => {
    setUserAvatarData(avatar);
    setIsAvatarOverwritten(true);
  };

  const handleModalClose = () => {
    resetFormFields();
    setSettingsModalVisibility(false);
    close();
  };

  return (
    <Root open={opened} onOpenChange={close}>
      <Portal>
        <Content asChild className="fixed">
          <div className="w-full h-[100vh] z-[99] top-0 left-0 right-0 bg-gray-900">
            <TopGradient />
            <div className="flex justify-between items-center px-[30px] py-[26px] relative z-10">
              <img src={`favicon.svg`} className="h-[48px] w-[48px] cursor-pointer filter" />
              <h3 className="text-gray-400 text-[14px] leading-[21px]">AIConsole settings</h3>
              <Button variant="secondary" onClick={handleModalClose} small>
                <Icon icon={X} />
                Close
              </Button>
            </div>

            <div className="h-[calc(100%-100px)] max-w-[720px] mx-auto relative flex flex-col justify-center gap-5">
              <GlobalSettingsUserSection
                email={emailFormValue}
                setEmail={setEmailFormValue}
                username={usernameFormValue}
                setUsername={setUsernameFormValue}
                setImage={handleSetAvatarImage}
              />
              <GlobalSettingsApiSection apiKey={apiKeyValue} setApiKey={setApiKeyValue} />
              <GlobalSettingsCodeSection isAutoRun={isAutoRun} setIsAutoRun={setIsAutoRun} />
              <div className="flex items-center justify-end gap-[10px] py-[40px]">
                <Button variant="secondary" bold onClick={handleModalClose}>
                  Cancel
                </Button>
                <Button onClick={save}>{validating ? 'Validating...' : 'Save'}</Button>
              </div>
            </div>
          </div>
        </Content>
      </Portal>
    </Root>
  );
};
