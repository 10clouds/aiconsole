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

import { RefreshCcw } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';

import { Icon } from '@/components/common/icons/Icon';
import { useChatStore } from '@/store/assets/chat/useChatStore';
import { useAssetStore } from '@/store/assets/useAssetStore';
import { Asset } from '@/types/assets/assetTypes';
import { cn } from '@/utils/common/cn';
import useIsHovered from '@/utils/common/useIsHovered';
import useMousePosition from '@/utils/common/useMousePosition';
import { COMMANDS } from '@/utils/constants';

const NUMBER_OF_DISPLAYED_EXAMPLES = 2;
const COLOR_PRIMARY_SEMITRANSPARENT = '#A67CFF40';

interface ExamplePromptProps {
  asset: Asset;
  example: string;
  onSelected: (asset: Asset, example: string) => () => void;
  showExamples: boolean;
  isSelected: boolean;
}

const ExamplePrompt: React.FC<ExamplePromptProps> = ({ asset, example, onSelected, showExamples, isSelected }) => {
  const ref = useRef<HTMLDivElement>(null);
  const mousePosition = useMousePosition(ref);
  const isHovered = useIsHovered(ref);

  return (
    <div
      className={cn(
        'bg-gray-900 w-1/3 m-2 p-6 h-40 max-w-[400px] cursor-pointer transition duration-300 ease-in-out transform hover:scale-105 rounded-xl flex flex-col justify-center items-center text-center border border-gray-700',
        !showExamples && 'opacity-0',
        showExamples && isSelected ? 'bg-gray-600' : '',
      )}
      onClick={onSelected(asset, example)}
      // it is not possible to declare tailwindcss class with a dynamic value
      style={{
        backgroundImage:
          !isSelected && isHovered
            ? `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, ${COLOR_PRIMARY_SEMITRANSPARENT} 0px, transparent 180px)`
            : '',
      }}
      ref={ref}
    >
      <p className="text-gray-100 text-md overflow-hidden line-clamp-5">{example}</p>
    </div>
  );
};

interface EmptyChatProps {
  textAreaRef: React.RefObject<HTMLTextAreaElement>;
}

export const EmptyChat = ({ textAreaRef }: EmptyChatProps) => {
  const chatOptions = useChatStore((state) => state.chat?.chat_options);
  const command = chatOptions?.draft_command;

  function isExampleCurrentlyActive(asset: Asset, example: string) {
    if (command !== example) {
      return false;
    }

    if (asset.type === 'agent') {
      if (chatOptions?.agent_id !== asset.id) {
        return false;
      }
    }

    if (asset.type === 'material') {
      if ((chatOptions?.materials_ids.length ?? 0) === 0 || chatOptions?.materials_ids[0] !== asset.id) {
        return false;
      }
    }

    if (!(chatOptions?.ai_can_add_extra_materials ?? true)) {
      return false;
    }

    return true;
  }

  // Chat options
  const { editCommand, submitCommand } = useChatStore((state) => state.actions);
  const updateChatOptions = useChatStore((state) => state.updateChatOptions);

  const assets = useAssetStore((state) => state.assets);
  const [lastExamples, setLastExamples] = useState<string[]>([]);
  const [showExamples, setShowExamples] = useState(true);

  const [examplePrompts, setExamplePrompts] = useState<{ asset: Asset; example: string }[]>([]);

  useEffect(() => {
    setLastExamples(examplePrompts.map(({ example }) => example));
  }, [examplePrompts]);

  const getExamplePrompts = useCallback(() => {
    const usageExamplesWithAsset = assets
      .flatMap((asset) => asset.usage_examples.map((example) => ({ asset, example })))
      .filter(({ asset, example }) => !lastExamples.includes(example) && asset.enabled);

    const randomExamplesWithAsset = usageExamplesWithAsset
      .sort(() => Math.random() - 0.5)
      .slice(0, NUMBER_OF_DISPLAYED_EXAMPLES);

    return randomExamplesWithAsset;
  }, [assets, lastExamples]);

  useEffect(() => {
    const randomExamplesWithAsset = getExamplePrompts();

    setExamplePrompts(randomExamplesWithAsset);
  }, []);

  const refreshUsageExamples = useCallback(() => {
    setShowExamples(false);
    setTimeout(() => {
      const randomExamplesWithAsset = getExamplePrompts();

      setExamplePrompts(randomExamplesWithAsset);
      setShowExamples(true);
    }, 300);
  }, [getExamplePrompts]);

  const onSelected = (asset: Asset, example: string) => () => {
    textAreaRef.current?.focus();

    //if is already selected, deselect
    if (isExampleCurrentlyActive(asset, example)) {
      //deselect
      editCommand('');
      updateChatOptions({ materials_ids: [], agent_id: '', ai_can_add_extra_materials: true });

      return;
    }

    if (asset.type == 'agent') {
      updateChatOptions({ agent_id: asset.id });
    } else {
      updateChatOptions({ agent_id: '' });
    }

    if (asset.type == 'material') {
      updateChatOptions({ materials_ids: [asset.id] });
    } else {
      updateChatOptions({ materials_ids: [] });
    }

    editCommand(example);
    updateChatOptions({ ai_can_add_extra_materials: true });
  };

  return (
    <section className="flex flex-col container mx-auto px-6 py-[64px] pb-[40px] select-none flex-grow h-full w-ful text-gray-300 ">
      <img src="chat-page-glow.png" className="absolute top-[75px] left-1/2 -z-[1] opacity-70" />
      <img src="chat-page-glow.png" className="absolute top-[75px] -left-1/2 -z-[1] opacity-70" />
      <p className="text-2xl font-extrabold	leading-[34px] text-white text-center mt-[100px] mb-[15px]">
        Hello. What can I help you with?
      </p>
      {examplePrompts.length >= 2 && (
        <div className=" w-full flex flex-row gap-3 justify-center items-center">
          <ExamplePrompt
            asset={examplePrompts[0].asset}
            example={examplePrompts[0].example}
            onSelected={onSelected}
            showExamples={showExamples}
            isSelected={isExampleCurrentlyActive(examplePrompts[0].asset, examplePrompts[0].example)}
          />
          or
          <ExamplePrompt
            asset={examplePrompts[1].asset}
            example={examplePrompts[1].example}
            onSelected={onSelected}
            showExamples={showExamples}
            isSelected={isExampleCurrentlyActive(examplePrompts[1].asset, examplePrompts[1].example)}
          />
        </div>
      )}
      <div className="flex items-center justify-center">
        <button
          className="flex items-center gap-2 justify-center cursor-pointer hover:text-white mt-[20px] text-md"
          onClick={refreshUsageExamples}
        >
          <Icon icon={RefreshCcw} width={16} height={16} />
        </button>
      </div>

      <div className="flex items-center justify-center gap-1 mt-10">
        <p>Need help?</p>
        <button
          className="text-secondary underline underline-offset-2 hover:text-secondary-dark"
          onClick={() => submitCommand(COMMANDS.GUIDE_ME)}
        >
          Guide me
        </button>
      </div>
    </section>
  );
};
