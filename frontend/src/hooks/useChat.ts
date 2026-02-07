/**
 * Custom hook for managing chat state and operations.
 *
 * Provides message history, loading states, and methods for
 * sending messages to the AI chatbot.
 */

"use client";

import { useState, useCallback } from "react";
import { chatApi, ChatMessage, ToolCallResult } from "@/lib/chat-api";
import { ApiError } from "@/lib/api";

export interface LocalMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCallResult[];
  isLoading?: boolean;
}

interface UseChatReturn {
  messages: LocalMessage[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
  loadConversation: (conversationId: string) => Promise<void>;
}

/**
 * Hook for managing chat interactions with the AI assistant.
 *
 * @example
 * ```tsx
 * const { messages, sendMessage, isLoading } = useChat();
 *
 * const handleSubmit = async (text: string) => {
 *   await sendMessage(text);
 * };
 * ```
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Send a message to the AI chatbot.
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      setError(null);
      setIsLoading(true);

      // Add user message immediately
      const userMessage: LocalMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      };

      // Add placeholder for assistant response
      const loadingMessage: LocalMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMessage, loadingMessage]);

      try {
        const response = await chatApi.sendMessage(
          content.trim(),
          conversationId ?? undefined
        );

        // Update conversation ID if this is a new conversation
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Replace loading message with actual response
        const assistantMessage: LocalMessage = {
          id: `assistant-${response.conversation_id}-${Date.now()}`,
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
          toolCalls:
            response.tool_calls.length > 0 ? response.tool_calls : undefined,
        };

        setMessages((prev) =>
          prev.map((msg) =>
            msg.isLoading ? assistantMessage : msg
          )
        );
      } catch (err) {
        // Remove loading message on error
        setMessages((prev) => prev.filter((msg) => !msg.isLoading));

        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Failed to send message. Please try again.");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  /**
   * Clear the current chat and start fresh.
   */
  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  /**
   * Load an existing conversation from the server.
   */
  const loadConversation = useCallback(async (convId: string) => {
    setError(null);
    setIsLoading(true);

    try {
      const conversation = await chatApi.getConversation(convId);

      setConversationId(conversation.id);
      setMessages(
        conversation.messages.map((msg: ChatMessage) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at),
        }))
      );
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to load conversation.");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    clearChat,
    loadConversation,
  };
}
