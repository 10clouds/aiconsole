/* eslint-disable @typescript-eslint/no-unused-vars */
import { ExecutionModeParamField, getExecutionModeParamsSchema } from '@/api/api/ExecutionModeAPI';
import { FormGroup } from '@/components/common/FormGroup';
import ImageUploader from '@/components/common/ImageUploader';
import { Select } from '@/components/common/Select';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { useAPIStore } from '@/store/useAPIStore';
import { Agent, Asset } from '@/types/assets/assetTypes';
import { EXECUTION_MODES, getExecutionMode } from '@/utils/assets/getExecutionMode';
import { useDebouncedFunction } from '@/utils/common/useDebouncedFunction';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { CodeInput } from '../CodeInput';
import { HelperLabel } from '../HelperLabel';
import { MarkdownSupported } from '../MarkdownSupported';
import { ErrorObject, TextInput } from '../TextInput';
import Checkbox from '@/components/common/Checkbox';

interface AgentFormProps {
  agent: Agent;
  avatarData: File | null;
  setAvatarData: React.Dispatch<React.SetStateAction<File | null>>;
  setIsAvatarOverwritten: React.Dispatch<React.SetStateAction<boolean>>;
  errors?: ErrorObject;
  setErrors?: React.Dispatch<React.SetStateAction<ErrorObject>>;
  onRevert: () => void;
  urlId: string;
}

// TODO: all commented lines are ready UI - integrate it with backend when ready
export const AgentForm = ({
  agent,
  errors,
  setErrors,
  avatarData: _avatarData,
  setAvatarData,
  setIsAvatarOverwritten,
  onRevert: _onRevert,
  urlId,
}: AgentFormProps) => {
  const agentRef = useRef(agent);
  const [hasFirstLoadedParamsSchema, setHasFirstLoadedParamsSchema] = useState<boolean>(false);
  const [avatarUrl, setAvatarUrl] = useState<string>('');
  const [paramsFields, setParamsFields] = useState<[string, ExecutionModeParamField][]>([]);
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const handleUsageChange = (value: string) => setSelectedAsset({ ...agent, usage: value });

  const getAndSetExecutionModeParamsSchema = useCallback(async (module_path: string, notify = true) => {
    let params = await getExecutionModeParamsSchema(module_path, notify);

    const currentAgent = agentRef.current;
    const paramsValues = currentAgent.execution_mode_params_values;

    params = params.map(([key, data]) => [
      key,
      {
        ...data,
        value: paramsValues[key] ?? data.value,
      },
    ]);

    setParamsFields(params);
  }, []);
  const debouncedGetExecutionModeParamsSchema = useDebouncedFunction(getAndSetExecutionModeParamsSchema, 1000);

  useEffect(() => {
    if (!hasFirstLoadedParamsSchema) {
      getAndSetExecutionModeParamsSchema(agent.execution_mode, false);
      setHasFirstLoadedParamsSchema(true);
    }
  }, [agent.execution_mode, hasFirstLoadedParamsSchema]);

  const hasAnyParams = paramsFields.length > 0;

  const setExecutionModeModulePathState = (value: string) => {
    debouncedGetExecutionModeParamsSchema(value);

    setSelectedAsset({
      ...agent,
      execution_mode: value,
    } as Asset);
  };

  const setExecutionModeParamValue = (key: string, value: any) => {
    setSelectedAsset({
      ...agent,
      execution_mode_params_values: {
        ...agent.execution_mode_params_values,
        [key]: value,
      },
    } as Asset);
  };

  const getBaseURL = useAPIStore((state) => state.getBaseURL);

  const executionMode = useMemo(() => getExecutionMode(agent.execution_mode), [agent.execution_mode]);

  const isCustomMode = executionMode === 'custom';

  const handleSetExecutionMode = (value: string) => {
    setErrors?.((prev) => ({ ...prev, executionMode: '' }));
    setExecutionModeModulePathState(value === 'custom' ? '' : value);
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
    const userAgentAvatarUrl = `${getBaseURL()}/api/assets/${urlId}/image?version=${agent?.version}`;
    setAvatarUrl(userAgentAvatarUrl);
  }, [urlId, agent.version, getBaseURL]);

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
              onChange={setExecutionModeModulePathState}
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
            {hasAnyParams && <div className="text-md font-semibold mb-4">Execution Mode Parameters</div>}
            {paramsFields.map(([key, data]) =>
              data.type === 'checkbox' ? (
                <Checkbox
                  key={key}
                  id={key}
                  label={data.title}
                  checked={data.value}
                  onChange={(newValue) => {
                    setParamsFields((prev) =>
                      prev.map(([k, v]) => {
                        if (k === key) {
                          return [k, { ...v, value: newValue }];
                        }
                        return [k, v];
                      }),
                    );
                    setExecutionModeParamValue(key, newValue);
                  }}
                />
              ) : (
                <TextInput
                  key={key}
                  label={data.title}
                  name={key}
                  required
                  type={data.type}
                  placeholder="Write text here"
                  setErrors={setErrors}
                  errors={errors}
                  value={data.value}
                  onChange={(newValue) => {
                    setParamsFields((prev) =>
                      prev.map(([k, v]) => {
                        if (k === key) {
                          return [k, { ...v, value: newValue }];
                        }
                        return [k, v];
                      }),
                    );
                    setExecutionModeParamValue(key, newValue);
                  }}
                  className="mb-[20px] leading-relaxed"
                />
              ),
            )}
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
