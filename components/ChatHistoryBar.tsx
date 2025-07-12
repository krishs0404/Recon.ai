import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Plus, Search, Book, Folder } from 'lucide-react';

interface ChatSession {
  id: string;
  title: string;
}

const projects = [
  { id: 'p1', name: 'Cold Email AI Assistant' },
  { id: 'p2', name: 'RentFlow' },
  { id: 'p3', name: "Krish's Comp Bio Research" },
  { id: 'p4', name: 'Patient Navigation App' },
  { id: 'p5', name: 'ML Model for Biomedical I...' },
];

export default function ChatHistoryBar({ onSelect, onNewChat, selectedId }: {
  onSelect: (id: string) => void;
  onNewChat: () => void;
  selectedId: string | null;
}) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem('chat_sessions');
    if (stored) setSessions(JSON.parse(stored));
  }, []);

  useEffect(() => {
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
  }, [sessions]);

  const handleNewChat = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: `Chat ${sessions.length + 1}`,
    };
    setSessions([newSession, ...sessions]);
    onNewChat();
  };

  return (
    <aside className="w-72 h-full bg-[#18181b] border-r border-[#23232a] flex flex-col select-none">
      {/* Logo */}
      <div className="flex flex-col items-center py-6">
        <Image src="/recon_logo.png" alt="Recon Logo" width={48} height={48} />
      </div>
      {/* Navigation */}
      <nav className="px-4 space-y-1">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-3 py-2 px-3 rounded-lg text-white bg-[#23232a] hover:bg-[#23232a]/80 font-semibold transition mb-1"
        >
          <Plus className="w-5 h-5" /> New chat
        </button>
        <button className="w-full flex items-center gap-3 py-2 px-3 rounded-lg text-gray-200 hover:bg-[#23232a]/80 transition">
          <Search className="w-5 h-5" /> Search chats
        </button>
        <button className="w-full flex items-center gap-3 py-2 px-3 rounded-lg text-gray-200 hover:bg-[#23232a]/80 transition">
          <Book className="w-5 h-5" /> Library
        </button>
      </nav>
      {/* Divider */}
      <div className="my-4 border-t border-[#23232a]" />
      {/* Projects */}
      <div className="px-4">
        <div className="text-xs text-gray-500 font-semibold mb-2 mt-2">Projects</div>
        <ul className="space-y-1">
          {projects.map((proj) => (
            <li key={proj.id} className="flex items-center gap-2 text-gray-200 py-1 px-2 rounded hover:bg-[#23232a]/80 cursor-pointer">
              <Folder className="w-4 h-4 text-gray-400" />
              <span className="truncate">{proj.name}</span>
            </li>
          ))}
        </ul>
      </div>
      {/* Divider */}
      <div className="my-4 border-t border-[#23232a]" />
      {/* Chats */}
      <div className="px-4 flex-1 overflow-y-auto">
        <div className="text-xs text-gray-500 font-semibold mb-2">Chats</div>
        {sessions.length === 0 ? (
          <div className="text-gray-500 p-4">No chats yet</div>
        ) : (
          <ul>
            {sessions.map((session) => (
              <li
                key={session.id}
                onClick={() => onSelect(session.id)}
                className={`px-3 py-2 cursor-pointer text-white rounded-lg hover:bg-[#23232a]/80 transition mb-1 ${selectedId === session.id ? 'bg-[#23232a]' : ''}`}
              >
                {session.title}
              </li>
            ))}
          </ul>
        )}
      </div>
      {/* Optional bottom section */}
      {/* <div className="p-4 border-t border-[#23232a] text-xs text-gray-500">View plans</div> */}
    </aside>
  );
} 