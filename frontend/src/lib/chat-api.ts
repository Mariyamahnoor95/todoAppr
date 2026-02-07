/**
 * Chat API client for AI chatbot communication.
 *
 * Provides type-safe methods for interacting with the chat endpoints.
 * Handles conversation management and message sending.
 */

import { ApiError, fetchApi } from "./api";

// Chat API Types
export interface ToolCallResult {
  tool: string;
  result: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCallResult[];
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string | null;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface ConversationDetail {
  id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

/**
 * Get the current user ID from the auth store.
 * Throws if user is not authenticated.
 */
async function getUserId(): Promise<string> {
  const { useAuthStore } = await import("@/lib/store");
  const user = useAuthStore.getState().user;
  if (!user?.id) {
    throw new ApiError(401, "Not authenticated");
  }
  return user.id;
}

/**
 * Chat API methods
 *
 * All endpoints use /api/{user_id}/... format.
 * JWT token is sent in Authorization header.
 */
export const chatApi = {
  /**
   * Send a message to the AI chatbot.
   * Creates a new conversation if conversation_id is not provided.
   */
  sendMessage: async (
    message: string,
    conversationId?: string
  ): Promise<ChatResponse> => {
    const userId = await getUserId();
    const body: ChatRequest = { message };
    if (conversationId) {
      body.conversation_id = conversationId;
    }

    return fetchApi<ChatResponse>(`/api/${userId}/chat`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  /**
   * Get list of user's conversations.
   */
  listConversations: async (params?: {
    limit?: number;
    offset?: number;
  }): Promise<ConversationListResponse> => {
    const userId = await getUserId();
    const queryParams = new URLSearchParams();
    if (params?.limit !== undefined)
      queryParams.append("limit", params.limit.toString());
    if (params?.offset !== undefined)
      queryParams.append("offset", params.offset.toString());

    const query = queryParams.toString();
    return fetchApi<ConversationListResponse>(
      `/api/${userId}/conversations${query ? `?${query}` : ""}`
    );
  },

  /**
   * Get a specific conversation with all messages.
   */
  getConversation: async (conversationId: string): Promise<ConversationDetail> => {
    const userId = await getUserId();
    return fetchApi<ConversationDetail>(
      `/api/${userId}/conversations/${conversationId}`
    );
  },

  /**
   * Delete a conversation.
   */
  deleteConversation: async (conversationId: string): Promise<void> => {
    const userId = await getUserId();
    await fetchApi<{ message: string }>(
      `/api/${userId}/conversations/${conversationId}`,
      { method: "DELETE" }
    );
  },
};
