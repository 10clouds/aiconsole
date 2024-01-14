import { useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import rehypeRaw from 'rehype-raw';
import { duotoneDark as vs2015 } from 'react-syntax-highlighter/dist/cjs/styles/prism';

import { BlinkingCursor } from '@/components/editables/chat/BlinkingCursor';
import { useChatStore } from '@/store/editables/chat/useChatStore';
import { useAPIStore } from '@/store/useAPIStore';
import { EditableContentMessage } from './EditableContentMessage';
import { AICMessage, AICMessageGroup } from '../../../../types/editables/chatTypes';
import { ToolCall } from './ToolCall';

const urlRegex = /^https?:\/\//;

interface MessageProps {
  group: AICMessageGroup;
  message: AICMessage;
}

export function MessageComponent({ message, group }: MessageProps) {
  const userMutateChat = useChatStore((state) => state.userMutateChat);
  const saveCommandAndMessagesToHistory = useChatStore((state) => state.saveCommandAndMessagesToHistory);
  const getBaseURL = useAPIStore((state) => state.getBaseURL);

  const handleRemoveClick = useCallback(() => {
    userMutateChat({
      type: 'DeleteMessageMutation',
      message_id: message.id,
    });
  }, [message.id, userMutateChat]);

  const handleSaveClick = useCallback(
    (content: string) => {
      userMutateChat({
        type: 'SetContentMessageMutation',
        message_id: message.id,
        content,
      });

      saveCommandAndMessagesToHistory(content, group.role === 'user');
    },
    [message.id, saveCommandAndMessagesToHistory, group.role, userMutateChat],
  );

  const submitCommand = useChatStore((state) => state.submitCommand);

  return (
    <div>
      <EditableContentMessage
        initialContent={message.content}
        handleAcceptedContent={handleSaveClick}
        handleRemoveClick={handleRemoveClick}
        hideControls
      >
        <div className="flex flex-col gap-2">
          {(message.content || message.is_streaming) && (
            <div className="max-w-[700px]">
              {group.role !== 'user' && (
                <div className="flex-grow">
                  <div className="prose prose-stone dark:prose-invert sidebar-typography w-full max-w-full">
                    <ReactMarkdown
                      urlTransform={null}
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        // eslint-disable-next-line @typescript-eslint/no-unused-vars
                        a: ({ node, href, ...props }) => {
                          if (href === 'command') {
                            const command = props.children[0]?.toString();
                            return (
                              <a
                                {...props}
                                className="text-secondary hover:text-secondary-light cursor-pointer"
                                onClick={() => {
                                  if (command) submitCommand(command);
                                }}
                              >
                                {props.children}
                              </a>
                            );
                          }
                          return (
                            <a
                              href={href}
                              {...props}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary"
                            >
                              {props.children}
                            </a>
                          );
                        },
                        img: ({ src, ...props }) => {
                          const imgSrc = urlRegex.test(src || '') ? src : `${getBaseURL()}/image?path=${src}`;

                          return (
                            <a href={imgSrc} target="_blank">
                              <img src={imgSrc} {...props} className=" max-w-xs rounded-md mr-5" alt={props.alt} />
                            </a>
                          );
                        },
                        code(props) {
                          // eslint-disable-next-line @typescript-eslint/no-unused-vars
                          const { children, className, inline, node, ...rest } = props;
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              {...rest}
                              style={vs2015}
                              children={String(children).replace(/\n$/, '')}
                              language={match[1]}
                              PreTag="div"
                            />
                          ) : (
                            <code {...rest} className={className}>
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                    {message.is_streaming && !message.content && message.tool_calls.length === 0 && <BlinkingCursor />}
                  </div>
                </div>
              )}

              {group.role === 'user' && (
                <div className="flex-grow">
                  {message.content.split('\n').map((line, index) => (
                    <span key={`line-${index}`} style={{ whiteSpace: 'pre-wrap' }}>
                      {line}
                      {index !== message.content.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {message.tool_calls.map((toolCall) => (
            <ToolCall key={toolCall.id} group={group} toolCall={toolCall} />
          ))}
        </div>
      </EditableContentMessage>
    </div>
  );
}
