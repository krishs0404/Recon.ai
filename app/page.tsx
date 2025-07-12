'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import Header from '@/components/Header';
import ChatHistoryBar from '@/components/ChatHistoryBar';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);

  const handleSelectSession = (id: string) => {
    setSelectedSession(id);
  };
  const handleNewChat = () => {
    setSelectedSession(null); // Optionally reset chat interface
  };

  return (
    <div className="flex flex-col h-screen bg-black">
      <Header />
      <div className="flex flex-1 bg-black">
        <ChatHistoryBar
          onSelect={handleSelectSession}
          onNewChat={handleNewChat}
          selectedId={selectedSession}
        />
        <main className="flex-1 flex flex-col bg-black">
          <ChatInterface isLoading={isLoading} setIsLoading={setIsLoading} />
        </main>
      </div>
    </div>
  );
} 