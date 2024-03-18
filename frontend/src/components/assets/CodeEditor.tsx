import React, { type ReactNode, useState } from 'react';
import MonacoEditor, { EditorProps, loader } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

import { cn } from '@/utils/common/cn';
import './CodeEditor.css';

monaco.editor.defineTheme('customCodeEditorTheme', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '#7a7a7a' },
    { token: 'keyword', foreground: '#569CD6' },
  ],
  colors: {
    'editor.background': '#1A1A1A',
    'editor.foreground': '#D4D4D4',
    'editorLineNumber.foreground': '#858585',
    'editor.selectionBackground': '#264F78',
  },
});

// Set the custom theme for Monaco Editor instances
// monaco.editor.setTheme('customCodeEditorTheme');

loader.config({ monaco });

interface CodeEditorProps extends Omit<EditorProps, 'theme' | 'onChange'> {
  withFullscreen?: boolean;
  labelContent?: ReactNode;
  label?: string;
  labelSize?: 'sm' | 'md';
  onChange?: (value: string) => void;
  readOnly?: boolean;
  isFocused?: boolean;
  maxHeight?: number;
  minHeight?: number;
  onBlur?: () => Promise<void>;
}

const DEFAULT_MAX_HEIGHT = 600;
const DEFAULT_MIN_HEIGHT = 120;

export const CodeEditor: React.FC<CodeEditorProps> = React.memo<CodeEditorProps>(
  ({
    withFullscreen = false,
    language = 'python',
    defaultValue = 'Write some text',
    onChange,
    onBlur,
    label,
    labelSize,
    labelContent,
    readOnly,
    isFocused,
    minHeight = DEFAULT_MIN_HEIGHT,
    maxHeight = DEFAULT_MAX_HEIGHT,
    ...props
  }) => {
    const [editorHeight, setEditorHeight] = useState<number>(minHeight);

    const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor) => {
      if (isFocused) {
        const lastLineNumber = editor.getModel()?.getLineCount() || 0;
        const lastColumn = editor.getModel()?.getLineLastNonWhitespaceColumn(lastLineNumber) || 0;
        editor.focus();
        editor.setPosition({ lineNumber: lastLineNumber, column: lastColumn });
      }

      const scrollEditorIntoView = () => {
        editor.getContainerDomNode().scrollIntoView();
      };

      editor.onDidFocusEditorText(() => {
        scrollEditorIntoView();
      });

      editor.onDidChangeModelContent(() => {
        onChange?.(editor.getValue());
        scrollEditorIntoView();
      });

      editor.onDidContentSizeChange(() => {
        const height = Math.min(editor.getContentHeight() || 0, maxHeight - 30) + 30;
        setEditorHeight(height);
      });

      editor.onDidBlurEditorText(() => {
        if (onBlur) {
          onBlur();
        }
      });
    };

    return (
      <div id="code-editor">
        <div className="mb-[10px] flex items-center">
          <label
            htmlFor={label}
            className={cn('py-3 flex', {
              'text-gray-300 text-sm': labelSize === 'sm',
              'text-white text-[15px]': labelSize === 'md',
            })}
          >
            {label}
          </label>
          {labelContent}
        </div>
        <MonacoEditor
          key={label}
          loading={false}
          defaultValue={defaultValue}
          height={editorHeight}
          language={language}
          options={{
            minimap: { enabled: false },
            automaticLayout: true,
            scrollBeyondLastLine: false,
            readOnly,
            fontSize: 15,
            trimAutoWhitespace: true,
            mouseWheelZoom: true,
            wordWrap: 'on',
            wrappingStrategy: 'advanced',
          }}
          wrapperProps={{
            className: cn(
              props.className,
              'border-gray-500 bg-gray-800 overflow-hidden border rounded-[8px] transition duration-100',
              'focus-within:border-gray-400',
            ),
          }}
          theme="vs-dark"
          onMount={handleEditorDidMount}
          {...props}
        />
      </div>
    );
  },
  (prevProps, nextProps) => {
    return prevProps.label === nextProps.label;
  },
);
