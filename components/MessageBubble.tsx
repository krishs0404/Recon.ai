import { cn } from '@/lib/utils';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';

  return (
    <div className={cn(
      "flex",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "rounded-lg px-4 py-2 max-w-md lg:max-w-lg xl:max-w-xl",
        isUser 
          ? "bg-primary-600 text-white" 
          : "bg-white border border-gray-200 text-gray-900"
      )}>
        <div className="whitespace-pre-wrap text-sm">
          {message.content}
        </div>
        <div className={cn(
          "text-xs mt-1",
          isUser ? "text-primary-100" : "text-gray-500"
        )}>
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
} 