'use client';

import { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
// import RateLimitStatus from './RateLimitStatus';
import { cn } from '@/lib/utils';

interface ChatInterfaceProps {
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatInterface({ isLoading, setIsLoading }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hi! I'm Recon, your networking assistant. Enter a LinkedIn URL or name, and I'll help you prepare for your networking call by analyzing their profile and recent activities.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');

  // New state for structured assistant output
  const [lastSummary, setLastSummary] = useState<string | null>(null);
  const [lastQuestions, setLastQuestions] = useState<string[] | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setLastSummary(null);
    setLastQuestions(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ linkedinUrl: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze profile');
      }

      const data = await response.json();
      setLastSummary(data.summary);
      setLastQuestions(data.questions);

      // Add a placeholder message for the summary (for chat history)
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.summary,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error while analyzing the profile. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full bg-black">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-0 py-4 space-y-4">
        {messages.map((message, idx) => (
          <div key={message.id} className="text-white text-base">
            {message.content}
          </div>
        ))}
        {/* Structured Output Section */}
        {lastSummary && (
          <div className="text-white text-base mt-8">
            <div className="mb-2 font-bold">Summary</div>
            <p className="mb-4 whitespace-pre-line">{lastSummary}</p>
            {lastQuestions && lastQuestions.length > 0 && (
              <div>
                <div className="mb-1 font-bold">Smart Questions</div>
                <ul className="list-disc pl-6">
                  {lastQuestions.map((q, i) => (
                    <li key={i}>{q}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="text-white text-base">
              <div className="flex items-center space-x-2">
                <Loader2 className="h-4 w-4 animate-spin text-white" />
                <span className="text-sm text-gray-300">
                  Analyzing profile and generating insights...
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
      {/* Input Form */}
      <div className="bg-black p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter LinkedIn URL or name..."
            className="flex-1 px-4 py-2 bg-black text-white placeholder-gray-500 rounded focus:outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              "px-4 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed transition-colors",
              !input.trim() || isLoading ? "opacity-50 cursor-not-allowed" : ""
            )}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
} 