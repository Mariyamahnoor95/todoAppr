/**
 * Chat component - Main chat interface wrapper.
 *
 * Provides the full chat experience with message history,
 * input field, and action buttons.
 */

"use client";

import { useEffect, useRef } from "react";
import { useChat, LocalMessage } from "@/hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Button } from "@/components/ui/button";

interface ChatProps {
  conversationId?: string;
}

export function Chat({ conversationId }: ChatProps) {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    loadConversation,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load existing conversation if provided
  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    }
  }, [conversationId, loadConversation]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center space-x-2">
          <BotIcon className="w-6 h-6 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Task Assistant
          </h2>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={clearChat}
          disabled={messages.length === 0}
        >
          New Chat
        </Button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((msg: LocalMessage) => (
              <ChatMessage
                key={msg.id}
                role={msg.role}
                content={msg.content}
                toolCalls={msg.toolCalls}
                isLoading={msg.isLoading}
                timestamp={msg.timestamp}
              />
            ))}
          </>
        )}

        {/* Error display */}
        {error && (
          <div className="flex justify-center mb-4">
            <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-4 py-2 rounded-lg text-sm">
              {error}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <ChatInput
        onSend={sendMessage}
        disabled={isLoading}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}

/**
 * Empty state shown when there are no messages.
 */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <BotIcon className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
        Hi! I&apos;m your Task Assistant
      </h3>
      <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm">
        I can help you manage your tasks using natural language. Try saying:
      </p>
      <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
        <SuggestionChip text="Add a task to buy groceries" />
        <SuggestionChip text="Show me all my tasks" />
        <SuggestionChip text="Mark task 1 as complete" />
        <SuggestionChip text="Delete the meeting task" />
      </div>
    </div>
  );
}

function SuggestionChip({ text }: { text: string }) {
  return (
    <div className="inline-block bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-full">
      &ldquo;{text}&rdquo;
    </div>
  );
}

function BotIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect x="3" y="11" width="18" height="10" rx="2" />
      <circle cx="12" cy="5" r="2" />
      <path d="M12 7v4" />
      <line x1="8" y1="16" x2="8" y2="16" />
      <line x1="16" y1="16" x2="16" y2="16" />
    </svg>
  );
}
