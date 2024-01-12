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

import { useToastsStore } from '@/store/common/useToastsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useState } from 'react';

export const useApiKey = () => {
  const [validating, setValidating] = useState(false);
  const isApiKeyValid = useSettingsStore((state) => state.isApiKeyValid);
  const validateApiKey = useSettingsStore((state) => state.validateApiKey);
  const saveSettings = useSettingsStore((state) => state.saveSettings);
  const showToast = useToastsStore((state) => state.showToast);
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);

  const saveOpenAiApiKey = async (key: string) => {
    await saveSettings({ openai_api_key: key }, !isProjectOpen);
  };

  const setApiKey = async (key: string) => {
    if (validating) return false;
    if (key) {
      setValidating(true);
      const isValidNow = await validateApiKey(key);
      setValidating(false);
      if (!isValidNow) {
        showApiError();

        return false;
      }
    } else {
      showApiError();
    }

    return true;
  };

  const showApiError = () => {
    showToast({
      title: 'Error',
      message: 'Invalid Open AI API key. Make sure that your API key has access to GPT-4',
      variant: 'error',
    });
  };

  return {
    setApiKey,
    saveOpenAiApiKey,
    showApiError,
    validating,
    isApiKeyValid,
  };
};
