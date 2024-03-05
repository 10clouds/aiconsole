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

import { AssetsAPI } from '@/api/api/AssetsAPI';
import { EmptyChat } from '@/components/assets/chat/EmptyChat';
import { MessageGroup } from '@/components/assets/chat/MessageGroup';
import { ContextMenu } from '@/components/common/ContextMenu';
import { QuestionMarkIcon } from '@/components/common/icons/QuestionMarkIcon';
import { SendRotated } from '@/components/common/icons/SendRotated';
import { useChatStore } from '@/store/assets/chat/useChatStore';
import { useToastsStore } from '@/store/common/useToastsStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { AICChat } from '@/types/assets/chatTypes';
import { useAssetContextMenu } from '@/utils/assets/useContextMenuForEditable';
import { cn } from '@/utils/common/cn';
import { COMMANDS } from '@/utils/constants';
import { ArrowDown, ReplyIcon, Square } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import ScrollToBottom, { useAnimating, useScrollToBottom, useSticky } from 'react-scroll-to-bottom';
import { v4 as uuidv4 } from 'uuid';
import { EditorHeader } from '../EditorHeader';
import { CommandInput } from './CommandInput';
import { Spinner } from './Spinner';

// Electron adds the path property to File objects
interface FileWithPath extends File {
  path: string;
}

export function ChatWindowScrollToBottomSave() {
  const scrollToBottom = useScrollToBottom();
  const setScrollChatToBottom = useChatStore((state) => state.setScrollChatToBottom);

  useEffect(() => {
    setScrollChatToBottom(scrollToBottom);
  }, [scrollToBottom, setScrollChatToBottom]);

  return <></>;
}

const ScrollToBottomButton = () => {
  const [isScrollingToBottom] = useAnimating();
  const [isSticky] = useSticky();

  const scrollToBottom = useScrollToBottom();

  return (
    <button
      className={cn(
        'absolute w-9 h-9 rounded-full bg-gray-600/70	-translate-x-1/2 left-1/2 top-[90%] flex justify-center items-center hover:bg-gray-600/90',
        (isScrollingToBottom || isSticky) && 'hidden',
      )}
      onClick={() => scrollToBottom()}
    >
      <ArrowDown />
    </button>
  );
};

export function ChatPage() {
  // Monitors params and initialises useChatStore.chat and useAssetStore.selectedAsset zustand stores
  const params = useParams();
  const id = params.id || '';
  const assetType = 'chat';
  const searchParams = useSearchParams()[0];
  const copyId = searchParams.get('copy');
  const forceRefresh = searchParams.get('forceRefresh'); // used to force a refresh
  const command = useChatStore((state) => state.commandHistory[state.commandIndex]);

  const chat = useChatStore((state) => state.chat);
  const setLastUsedChat = useChatStore((state) => state.setLastUsedChat);
  const loadingMessages = useChatStore((state) => state.loadingMessages);
  const isAnalysisRunning = useChatStore((state) => state.chat?.is_analysis_in_progress);
  const isExecutionRunning = useChatStore((state) => state.isExecutionRunning());
  const submitCommand = useChatStore((state) => state.submitCommand);
  const stopWork = useChatStore((state) => state.stopWork);
  const newCommand = useChatStore((state) => state.newCommand);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);
  const appendFilePathToCommand = useChatStore((state) => state.appendFilePathToCommand);
  const showToast = useToastsStore((state) => state.showToast);
  const menuItems = useAssetContextMenu({ asset: chat, assetType: 'chat' });
  const renameChat = useChatStore((state) => state.renameChat);
  const setChat = useChatStore((state) => state.setChat);
  const hasAnyCommandInput = command.trim() !== '';

  const [showSpinner, setShowSpinner] = useState(false);

  useEffect(() => {
    setShowSpinner(false);

    let timer: NodeJS.Timeout;
    if (!chat) {
      timer = setTimeout(() => {
        setShowSpinner(true);
      }, 500);
    }

    return () => clearTimeout(timer); // Cleanup the timer when the component unmounts or the dependencies change
  }, [loadingMessages, chat, isProjectLoading]); // Add dependencies that trigger the spinner

  useEffect(() => {
    const stopEvent = (e: Event) => {
      e.preventDefault();
      e.stopPropagation();
    };

    const handleDrop = (e: DragEvent) => {
      stopEvent(e);

      if (e.dataTransfer?.files) {
        appendFilePathToCommand((e.dataTransfer.files[0] as FileWithPath).path);
      }
    };

    document.addEventListener('dragover', stopEvent);

    document.addEventListener('drop', handleDrop);

    return () => {
      document.removeEventListener('dragover', stopEvent);

      document.removeEventListener('drop', handleDrop);
    };
  });

  useEffect(() => {
    if (chat) {
      setLastUsedChat(chat);
    }
  }, [chat, setLastUsedChat]);

  // Acquire the initial object
  useEffect(() => {
    if (copyId) {
      AssetsAPI.fetchAsset<AICChat>({ assetType, id: copyId }).then((orgChat) => {
        orgChat.id = uuidv4();
        orgChat.name = orgChat.name + ' (copy)';
        orgChat.title_edited = true;
        setChat(orgChat);
      });
    } else {
      //For id === 'new' This will get a default new asset
      AssetsAPI.fetchAsset<AICChat>({ assetType, id }).then((chat) => {
        setChat(chat);
      });
    }

    return () => {
      AssetsAPI.closeChat(id);
      useChatStore.setState({ chat: undefined });
    };
  }, [copyId, id, assetType, forceRefresh, setChat]);

  const isLastMessageFromUser =
    chat?.message_groups.length && chat.message_groups[chat.message_groups.length - 1].actor_id.type === 'user';

  useEffect(() => {
    //if there is exactly one text area focus on it
    const textAreas = document.getElementsByTagName('textarea');
    if (textAreas.length === 1) {
      textAreas[0].focus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return () => {
      stopWork();
    };
  }, [stopWork]); //Initentional trigger when chat_id changes

  const isProcessesAreNotRunning = !isExecutionRunning && !isAnalysisRunning;

  if (!chat) {
    return <div className="flex flex-1 justify-center items-center">{showSpinner && <Spinner />}</div>;
  }

  const handleRename = async (newName: string) => {
    if (newName !== chat.name) {
      const newChat = { ...chat, name: newName, title_edited: true } as AICChat;

      await renameChat(newChat);

      showToast({
        title: 'Overwritten',
        message: 'The chat has been successfully overwritten.',
        variant: 'success',
      });
    }
  };

  const getActionButton = () => {
    if (hasAnyCommandInput) {
      return {
        label: 'Send',
        icon: SendRotated,
        action: async () => {
          await submitCommand(command);
          await newCommand();
        },
      };
    } else {
      if (isProcessesAreNotRunning && isLastMessageFromUser) {
        return {
          label: 'Get reply',
          icon: ReplyIcon,
          action: () => submitCommand(``),
        };
      }

      if (isProcessesAreNotRunning && !isLastMessageFromUser) {
        return {
          label: 'Are you stuck? Let me guide you',
          icon: QuestionMarkIcon,
          action: () => submitCommand(COMMANDS.GUIDE_ME),
        };
      }

      return {
        label: 'Stop ' + (isAnalysisRunning ? ' analysis' : ' generation'),
        icon: Square,
        action: stopWork,
      };
    }
  };

  const { label: actionButtonLabel, icon: ActionButtonIcon, action: actionButtonAction } = getActionButton();

  return (
    <div className="flex flex-col w-full h-full max-h-full overflow-hidden">
      <ContextMenu options={menuItems}>
        <EditorHeader assetType="chat" editable={chat} onRename={handleRename} isChanged={false} />
      </ContextMenu>
      <div className="flex flex-col overflow-hidden h-full w-full">
        <div className="flex-1 overflow-hidden">
          {!isProjectLoading && !loadingMessages ? ( // This is needed because of https://github.com/compulim/react-scroll-to-bottom/issues/61#issuecomment-1608456508
            <ScrollToBottom
              className="h-full w-full overflow-auto-x"
              scrollViewClassName="main-chat-window flex-1"
              initialScrollBehavior="auto"
              mode={'bottom'}
              followButtonClassName="hidden"
            >
              <ChatWindowScrollToBottomSave />
              {chat.message_groups.length === 0 ? (
                <EmptyChat />
              ) : (
                chat.message_groups.map((group) => <MessageGroup group={group} key={group.id} />)
              )}
              <ScrollToBottomButton />
            </ScrollToBottom>
          ) : (
            <Spinner />
          )}
        </div>
        <CommandInput
          className="mt-auto"
          actionIcon={ActionButtonIcon}
          actionLabel={actionButtonLabel}
          onSubmit={actionButtonAction}
        />
      </div>
    </div>
  );
}
