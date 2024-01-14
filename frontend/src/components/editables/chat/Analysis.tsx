import { Icon } from '@/components/common/icons/Icon';
import { AICMessageGroup } from '@/types/editables/chatTypes';
import { cn } from '@/utils/common/cn';
import { XIcon } from 'lucide-react';

export const AnalysisClosed = ({ group, onClick }: { group: AICMessageGroup; onClick: () => void }) => {
  const onClick2 = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  return group.analysis || group.task ? (
    <img onClick={onClick2} src={`favicon.svg`} className="h-[18px] w-[18px] filter cursor-pointer mt-2" />
  ) : (
    <></>
  );
};

export const AnalysisOpened = ({ group, onClick }: { group: AICMessageGroup; onClick: () => void }) => {
  const onClick2 = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick();
  };

  return group.analysis || group.task ? (
    <div
      onClick={onClick2}
      className={cn(
        'flex flex-col text-grayPurple-300 rounded-[20px] px-[15px] pt-[8px] pb-[10px] w-full text-[14px] border border-grayPurple-800 transition duration-150 cursor-pointer',
        'p-[30px] max-w-[700px] max-h-max analysis-gradient border-grayPurple-600',
      )}
    >
      <div className="flex justify-between">
        <div className="flex gap-[10px] items-center">
          <img src={`favicon.svg`} className="h-[18px] w-[18px] filter" />
          AI Analysis process
        </div>
        <Icon icon={XIcon} className="text-gray-400" />
      </div>
      <div className="mt-[20px]">
        {group.analysis}{' '}
        {group.task && (
          <span className="text-white inline-block">
            <br /> Next step: <span className="text-purple-400 leading-[24px]">{group.task}</span>
          </span>
        )}
      </div>
    </div>
  ) : (
    <> </>
  );
};
