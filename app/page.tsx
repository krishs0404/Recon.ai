'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import Header from '@/components/Header';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-black">
      <Header />
      <main className="flex-1 flex flex-col bg-black">
        <ChatInterface isLoading={isLoading} setIsLoading={setIsLoading} />
      </main>
    </div>
  );
} 