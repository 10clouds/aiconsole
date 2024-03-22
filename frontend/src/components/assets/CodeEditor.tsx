import { type ReactNode, useState } from 'react';
import AceEditor from 'react-ace';
import { Maximize2, Minimize2 } from 'lucide-react';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/mode-markdown';
import 'ace-builds/src-noconflict/theme-github_dark';
import 'ace-builds/src-noconflict/ext-language_tools';
import { type Ace } from 'ace-builds';

import { cn } from '@/utils/common/cn';
import { Icon } from '../common/icons/Icon';
import { CodeEditorFullScreen } from './CodeEditorFullScreen';

interface CodeEditorProps {
  value: string | ReactNode;
  withFullscreen?: boolean;
  labelContent?: ReactNode;
  label?: string;
  labelSize?: 'sm' | 'md';
  onChange?: (value: string) => void;
  readOnly?: boolean;
  isFocused?: boolean;
  maxHeight?: number;
  onBlur?: () => Promise<void>;
  transparent?: boolean;
  codeLanguage?: string;
  debounceDelay?: number;
}

export function CodeEditor({
  codeLanguage = 'python',
  transparent = false,
  withFullscreen = false,
  debounceDelay = 0,
  maxHeight = Infinity,
  readOnly,
  isFocused,
  value,
  onChange,
  onBlur,
  label,
  labelSize,
  labelContent,
}: CodeEditorProps) {
  const [isFullscreenOpen, setIsFullscreenOpen] = useState<boolean>(false);

  const showLineNumbers = codeLanguage !== 'text' && codeLanguage !== 'markdown';
  const isProgrammingLang = codeLanguage === 'python';

  const toggleFullscreen = () => {
    setIsFullscreenOpen((prev) => !prev);
  };

  const CodeInput = (height: number) => {
    const handleLoad = (editor: Ace.Editor) => {
      editor.renderer.setPadding(20);

      const lineHeight = editor.renderer.lineHeight;
      const maxLines = height !== Infinity ? height / lineHeight : Infinity;
      editor.setOption('maxLines', maxLines);
    };

    return (
      <div className="relative">
        {typeof value === 'string' ? (
          <AceEditor
            className={cn('border border-gray-500 font-mono text-sm bg-gray-800 rounded-[8px] ', {
              'focus-within:bg-gray-600 focus-within:border-gray-400 transition-colors duration-100': !transparent,
              'hover:bg-gray-600 hover:border-gray-400': !readOnly && !transparent,
              'pointer-events-none opacity-[0.7]': readOnly,
              'bg-transparent outline-none border-0': transparent,
            })}
            theme="github_dark"
            placeholder="Write some text"
            width="100%"
            name="ace-editor"
            showGutter={showLineNumbers}
            mode={codeLanguage}
            focus={isFocused}
            value={value}
            debounceChangePeriod={debounceDelay}
            readOnly={readOnly}
            enableLiveAutocompletion={isProgrammingLang}
            onBlur={onBlur}
            onLoad={handleLoad}
            onChange={onChange}
            onFocus={(_, editor) => editor?.scrollPageDown}
            scrollMargin={[12, 12, 20, 20]}
            showPrintMargin={false}
            setOptions={{
              highlightGutterLine: false,
              highlightActiveLine: false,
              showPrintMargin: false,
              wrap: true,
              enableBasicAutocompletion: true,
              enableSnippets: false,
              tabSize: 2,
              fontSize: '15px',
              displayIndentGuides: !readOnly,
            }}
          />
        ) : (
          value
        )}

        {withFullscreen && (
          <Icon
            icon={isFullscreenOpen ? Minimize2 : Maximize2}
            width={24}
            height={24}
            className="absolute right-[25px] bottom-[10px] cursor-pointer text-gray-300 hover:text-white"
            onClick={toggleFullscreen}
          />
        )}
      </div>
    );
  };

  return (
    <>
      <div className="mb-[10px] flex items-center">
        <label
          htmlFor="ace-editor"
          className={cn('py-3 flex', {
            'text-gray-300 text-sm': labelSize === 'sm',
            'text-white text-[15px]': labelSize === 'md',
          })}
        >
          {label}
        </label>
        {labelContent}
      </div>

      {!isFullscreenOpen ? (
        CodeInput(maxHeight)
      ) : (
        <CodeEditorFullScreen setOpen={setIsFullscreenOpen} open={isFullscreenOpen}>
          {CodeInput(600)}
        </CodeEditorFullScreen>
      )}
    </>
  );
}
