/* eslint-disable @typescript-eslint/no-unused-vars */
import { FormGroup } from '@/components/common/FormGroup';
import ImageUploader from '@/components/common/ImageUploader';
import { Select } from '@/components/common/Select';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { useAPIStore } from '@/store/useAPIStore';
import { Agent, Asset } from '@/types/assets/assetTypes';
import { EXECUTION_MODES, getExecutionMode } from '@/utils/assets/getExecutionMode';
import { useEffect, useMemo, useState } from 'react';
import { CodeInput } from '../CodeInput';
import { HelperLabel } from '../HelperLabel';
import { MarkdownSupported } from '../MarkdownSupported';
import { ErrorObject, TextInput } from '../TextInput';

interface AgentFormProps {
  agent: Agent;
  avatarData: File | null;
  setAvatarData: React.Dispatch<React.SetStateAction<File | null>>;
  isAvatarOverwritten: boolean;
  setIsAvatarOverwritten: React.Dispatch<React.SetStateAction<boolean>>;
  errors?: ErrorObject;
  setErrors?: React.Dispatch<React.SetStateAction<ErrorObject>>;
  onRevert: () => void;
}

// TODO: all commented lines are ready UI - integrate it with backend when ready
export const AgentForm = ({
  agent,
  errors,
  setErrors,
  avatarData: _avatarData,
  setAvatarData,
  isAvatarOverwritten,
  setIsAvatarOverwritten,
  onRevert: _onRevert,
}: AgentFormProps) => {
  const [avatarUrl, setAvatarUrl] = useState<string>('');
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const handleUsageChange = (value: string) => setSelectedAsset({ ...agent, usage: value });
  const setExecutionModeState = (value: string) => setSelectedAsset({ ...agent, execution_mode: value } as Asset);
  const getBaseURL = useAPIStore((state) => state.getBaseURL);

  const executionMode = useMemo(() => getExecutionMode(agent.execution_mode), [agent.execution_mode]);
  const isCustomMode = executionMode === 'custom';

  const handleSetExecutionMode = (value: string) => {
    setErrors?.((prev) => ({ ...prev, executionMode: '' }));
    setExecutionModeState(value === 'custom' ? '' : value);
  };

  const setAsset = (value: string) =>
    setSelectedAsset({
      ...agent,
      system: value,
    } as Agent);

  const handleSetImage = (avatar: File) => {
    setAvatarData(avatar);
    setIsAvatarOverwritten(true);
  };

  useEffect(() => {
    // new Date is used to refresh image url
    if (!isAvatarOverwritten) {
      const userAgentAvatarUrl = `${getBaseURL()}/api/assets/${agent.id}/image?version=${agent?.version}`;
      setAvatarUrl(userAgentAvatarUrl);
    }
  }, [agent.id, agent.version, getBaseURL, isAvatarOverwritten]);

  return (
    <>
      <div className="flex gap-[20px]">
        <ImageUploader
          currentImage={avatarUrl}
          onUpload={(avatar: string) => handleSetImage(new File([avatar], 'avatar'))}
        />
        <FormGroup className="w-full">
          <TextInput
            label="Usage"
            name="usage"
            fullWidth
            placeholder="Write text here"
            value={agent.usage}
            className="w-full min-h-[90px]"
            onChange={handleUsageChange}
            helperText="Usage is used to help identify when this agent should be used. "
            resize
          />
          <MarkdownSupported />
        </FormGroup>
      </div>
      <div className="flex gap-[20px]">
        <FormGroup className="w-full h-full flex-col">
          <div className="flex flex-col flex-1">
            <TextInput
              label="Execution mode"
              name="executionMode"
              required
              placeholder="Write text here"
              setErrors={setErrors}
              errors={errors}
              value={agent.execution_mode}
              onChange={setExecutionModeState}
              className="mb-[20px] leading-relaxed"
              helperText="a Python module governing how the agent behaves."
              hidden={!isCustomMode}
              labelChildren={
                <Select
                  key={executionMode}
                  options={EXECUTION_MODES}
                  placeholder="Choose execution mode"
                  onChange={handleSetExecutionMode}
                  initialValue={executionMode}
                />
              }
            />
            <CodeInput
              label="System prompt"
              labelContent={
                <HelperLabel
                  helperText="System prompt will be injected at the begining of a context"
                  className="py-[13px]"
                />
              }
              value={agent.system}
              withFullscreen
              codeLanguage="markdown"
              maxHeight={'calc(100vh - 200px)'}
              onChange={setAsset}
            />
          </div>
          <MarkdownSupported />
        </FormGroup>
      </div>
    </>
  );
};
