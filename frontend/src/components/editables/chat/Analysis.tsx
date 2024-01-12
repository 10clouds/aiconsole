import { X } from 'lucide-react';
import { Icon } from '@/components/common/icons/Icon';
import { cn } from '@/utils/common/cn';
import { useState } from 'react';
import { AICMessageGroup } from '@/types/editables/chatTypes';

export const Analysis = ({ group }: { group: AICMessageGroup }) => {
  const [isOpen, setIsOpen] = useState(true);

  const open = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    e.stopPropagation();
    setIsOpen(true);
  };

  const close = (e: React.MouseEvent<SVGSVGElement, MouseEvent>) => {
    e.stopPropagation();
    setIsOpen(false);
  };

  return group.analysis || group.task ? (
    <div
      onClick={open}
      className={cn(
        'flex flex-col text-grayPurple-300 rounded-[20px] px-[15px] pt-[8px] pb-[10px] w-full text-[14px] border border-grayPurple-800 transition duration-150',
        isOpen
          ? 'p-[30px] max-w-[700px] max-h-max analysis-gradient border-grayPurple-600'
          : 'max-w-[190px] max-h-[40px] cursor-pointer bg-grayPurple-800 group-hover:border-purple-400 group-hover:shadow-md group-hover:bg-grayPurple-700 group-hover:text-white',
      )}
    >
      <div className="flex justify-between">
        <div className="flex gap-[10px] items-center">
          <img src={`favicon.svg`} className="h-[18px] w-[18px] cursor-pointer filter" />
          AI Analysis process
        </div>
        {isOpen && <Icon icon={X} onClick={close} className="text-gray-400 cursor-pointer" />}
      </div>
      {isOpen ? (
        <div className="mt-[20px]">
          {group.analysis}{' '}
          {group.task && (
            <span className="text-white inline-block">
              <br /> Next step: <span className="text-purple-400 leading-[24px]">{group.task}</span>
            </span>
          )}
        </div>
      ) : null}
    </div>
  ) : (
    <></>
  );
};
