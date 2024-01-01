import { useChatStore } from '@/store/editables/chat/useChatStore';
import { BlinkingCursor } from './BlinkingCursor';
import { cn } from '@/utils/common/cn';

export const Analysis = () => {
  const thinkingProcess = useChatStore((store) => store.analysis.thinking_process);
  const nextStep = useChatStore((store) => store.analysis.next_step);

  return (
    <div
      className={cn(
        'absolute pt-[80px] pb-[30px] flex flex-col gap-[10px] items-end bottom-0 right-0 guide-bg-shadow w-full',
      )}
    >
      <div className="rounded-lg border border-gray-600 guide-gradient p-[20px] text-[15px] text-gray-300 leading-[24px] w-full max-w-[700px] mx-auto animate-fadeInUp">
        {thinkingProcess}
        {nextStep && (
          <span className="text-white">
            <br /> Next step: <span className="text-purple-400 leading-[24px]">{nextStep}</span>
          </span>
        )}
        &nbsp;
        <BlinkingCursor />
      </div>
    </div>
  );
};
