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

import { EditablesAPI } from '@/api/api/EditablesAPI';
import { EmptyChat } from '@/components/editables/chat/EmptyChat';
import { MessageGroup } from '@/components/editables/chat/MessageGroup';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useProjectStore } from '@/store/projects/useProjectStore';
import { Chat } from '@/types/editables/chatTypes';
import { cn } from '@/utils/common/cn';
import { useChat } from '@/utils/editables/useChat';
import { useEditableObjectContextMenu } from '@/utils/editables/useContextMenuForEditable';
import { ReplyIcon, Square } from 'lucide-react';
import { useEffect } from 'react';
import { useParams, useSearchParams, unstable_useBlocker as useBlocker } from 'react-router-dom';
import ScrollToBottom, { useAnimating, useScrollToBottom, useSticky } from 'react-scroll-to-bottom';
import { v4 as uuidv4 } from 'uuid';
import { EditorHeader } from '../EditorHeader';
import { CommandInput } from './CommandInput';
import { Analysis } from './Analysis';
import { ArrowDown } from 'lucide-react';
import { SendRotated } from '@/components/common/icons/SendRotated';
import { useToastsStore } from '@/store/common/useToastsStore';
import { ContextMenu } from '@/components/common/ContextMenu';
import AlertDialog from '@/components/common/AlertDialog';
import { QuestionMarkIcon } from '@/components/common/icons/QuestionMarkIcon';
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
  const editableObjectType = 'chat';
  const searchParams = useSearchParams()[0];
  const copyId = searchParams.get('copy');
  const forceRefresh = searchParams.get('forceRefresh'); // used to force a refresh
  const command = useChatStore((state) => state.commandHistory[state.commandIndex]);

  const chat = useChatStore((state) => state.chat);
  const setLastUsedChat = useChatStore((state) => state.setLastUsedChat);
  const loadingMessages = useChatStore((state) => state.loadingMessages);
  const isAnalysisRunning = useChatStore((state) => state.chat?.is_analysis_in_progress);
  const isExecutionRunning = useChatStore((state) => state.isExecutionRunning());
  const stopWork = useChatStore((state) => state.stopWork);
  const submitCommand = useChatStore((state) => state.submitCommand);
  const newCommand = useChatStore((state) => state.newCommand);
  const isProjectOpen = useProjectStore((state) => state.isProjectOpen);
  const isProjectLoading = useProjectStore((state) => state.isProjectLoading);
  const appendFilePathToCommand = useChatStore((state) => state.appendFilePathToCommand);
  const showToast = useToastsStore((state) => state.showToast);
  const menuItems = useEditableObjectContextMenu({ editable: chat, editableObjectType: 'chat' });
  const { setChat, renameChat } = useChat();

  const blocker = useBlocker(isAnalysisRunning || isExecutionRunning);

  const { reset, proceed, state: blockerState } = blocker || {};

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
      EditablesAPI.fetchEditableObject<Chat>({ editableObjectType, id: copyId }).then((orgChat) => {
        orgChat.id = uuidv4();
        orgChat.name = orgChat.name + ' (copy)';
        orgChat.title_edited = true;
        setChat(orgChat);
      });
    } else {
      //For id === 'new' This will get a default new asset
      EditablesAPI.fetchEditableObject<Chat>({ editableObjectType, id }).then((chat) => {
        setChat(chat);
      });
    }

    return () => {
      useChatStore.setState({ chat: undefined });
    };
  }, [copyId, id, editableObjectType, forceRefresh, setChat]);

  const isLastMessageFromUser =
    chat?.message_groups.length && chat.message_groups[chat.message_groups.length - 1].agent_id === 'user';

  useEffect(() => {
    //if there is exactly one text area focus on it
    const textAreas = document.getElementsByTagName('textarea');
    if (textAreas.length === 1) {
      textAreas[0].focus();
    }

    return () => {
      stopWork();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chat?.id, isProjectOpen]); //Initentional trigger when chat_id changes

  if (!chat) {
    return (
      <div className="flex flex-1 justify-center items-center">
        <Spinner width={40} height={40} />
      </div>
    );
  }

  const handleRename = async (newName: string) => {
    if (newName !== chat.name) {
      const newChat = { ...chat, name: newName, title_edited: true } as Chat;

      await renameChat(newChat);

      showToast({
        title: 'Renamed',
        message: 'renamed',
        variant: 'success',
      });
    }
  };

  const isProcessesAreNotRunning = !isExecutionRunning && !isAnalysisRunning;
  const hasAnyCommandInput = command.trim() !== '';

  const getActionButton = () => {
    if (hasAnyCommandInput || chat.message_groups.length === 0) {
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
          action: () =>
            submitCommand(
              `I need help with using AIConsole, can you suggest what can I do from this point in the conversation?`,
            ),
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
    <div className="flex flex-col w-full h-full max-h-full overflow-auto">
      <ContextMenu options={menuItems}>
        <EditorHeader editableObjectType="chat" editable={chat} onRename={handleRename} isChanged={false} />
      </ContextMenu>

      <div className="flex-grow overflow-auto">
        <div className="flex w-full h-full flex-col justify-between downlight">
          {!isProjectLoading && !loadingMessages ? ( // This is needed because of https://github.com/compulim/react-scroll-to-bottom/issues/61#issuecomment-1608456508
            <ScrollToBottom
              className="h-full overflow-y-auto flex flex-col"
              scrollViewClassName="main-chat-window"
              initialScrollBehavior="auto"
              mode={'bottom'}
              followButtonClassName="hidden"
            >
              <ChatWindowScrollToBottomSave />
              {chat.message_groups.length === 0 ? (
                <EmptyChat />
              ) : (
                <div>
                  <ScrollToBottomButton />
                  {chat.message_groups.map((group) => (
                    <MessageGroup group={group} key={group.id} />
                  ))}
                </div>
              )}

              {isAnalysisRunning ? <Analysis /> : null}
            </ScrollToBottom>
          ) : (
            <div className="h-full overflow-y-auto flex flex-col"></div>
          )}

          <CommandInput
            className="flex-none"
            actionIcon={ActionButtonIcon}
            actionLabel={actionButtonLabel}
            onSubmit={actionButtonAction}
          />
          <AlertDialog
            title="Are you sure you want to exit this chat?"
            isOpen={blockerState === 'blocked'}
            onClose={reset}
            onConfirm={proceed}
          >
            {`The response is being generated.\nClosing the window cancels the process.`}
          </AlertDialog>
        </div>
      </div>
    </div>
  );
}
