import { EditableObject, EditableObjectType } from '@/types/editables/assetTypes';
import { getEditableObjectIcon } from '@/utils/editables/getEditableObjectIcon';
import { useState } from 'react';
import InlineEditableObjectName from './InlineEditableObjectName';
import { cn } from '@/utils/common/cn';
import { getEditableObjectType } from '@/utils/editables/getEditableObjectType';
import { Button } from '../common/Button';
import { ArrowLeftToLine } from 'lucide-react';
import { Icon } from '../common/icons/Icon';
import { useNavigate } from 'react-router-dom';
import { useChatStore } from '@/store/editables/chat/useChatStore';

interface EditorHeaderProps {
  editable?: EditableObject;
  onRename: (newName: string) => void;
  children?: React.ReactNode;
  isChanged?: boolean;
  editableObjectType: EditableObjectType;
}

export function EditorHeader({ editable, onRename, children, isChanged, editableObjectType }: EditorHeaderProps) {
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  const AssetIcon = getEditableObjectIcon(editable);
  const editableType = getEditableObjectType(editable);
  const lastUsedChat = useChatStore((state) => state.lastUsedChat);

  const goBack = () => {
    if (lastUsedChat) {
      navigate(`/chats/${lastUsedChat.id}`);
    }
  };

  if (!editable) {
    return <div className="flex flex-col w-full h-full items-center justify-center"></div>;
  }

  return (
    <div className="flex border-b border-gray-600 w-full">
      {editableObjectType !== 'chat' && lastUsedChat ? (
        <Button
          variant="tertiary"
          classNames="py-0 px-[20px] border-0 border-r border-gray-600 rounded-none"
          onClick={goBack}
        >
          <Icon icon={ArrowLeftToLine} /> Back
        </Button>
      ) : null}
      <div className="px-[20px] py-[13px] w-full flex flex-row gap-[10px] cursor-pointer  bg-gray-90 shadow-md items-center overflow-clip relative">
        <div onClick={() => setIsEditing(true)} className="flex flex-row gap-[10px] items-center w-full">
          <AssetIcon
            className={cn(
              'flex-none',
              editableType === 'chat' && 'text-chat',
              editableType === 'agent' && 'text-agent',
              editableType === 'material' && 'text-material',
            )}
          />
          <div
            className={cn(
              'absolute bottom-[-20px] left-[15px] opacity-[0.3] blur-[10px]  h-[34px] w-[34px] group-hover:block',
              editableObjectType === 'chat' && 'fill-chat bg-chat',
              editableObjectType === 'agent' && 'fill-agent bg-agent',
              editableObjectType === 'material' && 'fill-material bg-material',
            )}
          />
          <InlineEditableObjectName
            editableObject={editable}
            onRename={onRename}
            isEditing={isEditing}
            setIsEditing={setIsEditing}
            className={'flex-grow truncate ' + (isChanged ? ' italic font-bold ' : '')}
          />
        </div>
        <div className="self-end text-gray-400 text-[15px] min-w-fit">{children}</div>
      </div>
    </div>
  );
}
