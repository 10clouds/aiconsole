/* eslint-disable @typescript-eslint/no-unused-vars */
import { FormGroup } from '@/components/common/FormGroup';
import { Select } from '@/components/common/Select';
import { useAssetStore } from '@/store/editables/asset/useAssetStore';
import { Agent, Asset } from '@/types/editables/assetTypes';
import { useMemo, useState } from 'react';
import { CodeInput } from './CodeInput';
import { HelperLabel } from './HelperLabel';
import { ErrorObject, TextInput } from './TextInput';

const executionModes = [
  {
    value: 'aiconsole.core.chat.execution_modes.normal:execution_mode',
    label: 'Normal - conversational agent',
  },
  {
    value: 'aiconsole.core.chat.execution_modes.interpreter:execution_mode',
    label: 'Interpreter - code running agent',
  },
  {
    value: 'custom',
    label: 'Custom - (eg. custom.custom:custom_mode)',
  },
];

interface AgentFormProps {
  agent: Agent;
  errors?: ErrorObject;
  setErrors?: React.Dispatch<React.SetStateAction<ErrorObject>>;
}

// TODO: all commented lines are ready UI - integrate it with backend when ready
export const AgentForm = ({ agent, errors, setErrors }: AgentFormProps) => {
  const [executionMode, setExecutionMode] = useState('');
  const [customExecutionMode, setCustomExecutionMode] = useState('');
  const setSelectedAsset = useAssetStore((state) => state.setSelectedAsset);
  const handleUsageChange = (value: string) => setSelectedAsset({ ...agent, usage: value });
  const setExecutionModeState = (value: string) => setSelectedAsset({ ...agent, execution_mode: value } as Asset);

  const isCustomMode = useMemo(() => executionMode === 'custom', [executionMode]);

  const handleSetExecutionMode = (value: string) => {
    setExecutionMode(value);
    if (!isCustomMode) {
      setCustomExecutionMode('');
      setErrors?.((prev) => ({ ...prev, executionMode: '' }));
      setExecutionModeState(value);
    }
  };

  const handleCustomExecutionModeChange = (value: string) => {
    setCustomExecutionMode(value);
    setExecutionModeState(value);
  };

  const setAsset = (value: string) =>
    setSelectedAsset({
      ...agent,
      system: value,
    } as Agent);

  return (
    <>
      <div className="flex gap-[20px]">
        {/* <ImageUploader /> */}
        <FormGroup horizontal>
          <TextInput
            label="Usage"
            name="usage"
            fullWidth
            placeholder="Write text here"
            value={agent.usage}
            className="w-full"
            onChange={handleUsageChange}
            helperText="Usage is used to help identify when this agent should be used. "
            resize
          />
        </FormGroup>
      </div>
      <div className="flex gap-[20px]">
        <FormGroup className="w-full h-full flex">
          <div className="flex-1">
            <TextInput
              label="Execution mode"
              name="executionMode"
              required
              placeholder="Write text here"
              setErrors={setErrors}
              errors={errors}
              value={customExecutionMode}
              onChange={handleCustomExecutionModeChange}
              className="mb-[20px] leading-relaxed"
              helperText="a Python module governing how the agent behaves."
              hidden={!isCustomMode}
              labelChildren={
                <Select
                  options={executionModes}
                  placeholder="Choose execution mode"
                  onChange={handleSetExecutionMode}
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
              maxHeight={isCustomMode ? 'calc(100% - 120px)' : 'calc(100% - 200px)'}
              onChange={setAsset}
            />
          </div>
        </FormGroup>
      </div>
    </>
  );
};
