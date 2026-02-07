/**
 * ChatMessage component for displaying individual chat messages.
 *
 * Renders user and assistant messages with appropriate styling,
 * and displays tool call information when present.
 */

"use client";

import { cn } from "@/lib/utils";
import { ToolCallResult } from "@/lib/chat-api";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCallResult[];
  isLoading?: boolean;
  timestamp?: Date;
}

export function ChatMessage({
  role,
  content,
  toolCalls,
  isLoading,
  timestamp,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-3",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
        )}
      >
        {/* Loading indicator */}
        {isLoading ? (
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
            <span className="text-sm text-gray-500">Thinking...</span>
          </div>
        ) : (
          <>
            {/* Message content */}
            <p className="text-sm whitespace-pre-wrap">{content}</p>

            {/* Tool calls display */}
            {toolCalls && toolCalls.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Actions performed:
                </p>
                <div className="space-y-1">
                  {toolCalls.map((tc, index) => {
                    const status = tc.result.status as string | undefined;
                    return (
                      <div
                        key={index}
                        className="text-xs bg-gray-200 dark:bg-gray-700 rounded px-2 py-1"
                      >
                        <span className="font-medium">{formatToolName(tc.tool)}</span>
                        {status && (
                          <span className="ml-2 text-green-600 dark:text-green-400">
                            ✓ {status}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Timestamp */}
            {timestamp && (
              <p className="mt-1 text-xs opacity-60">
                {formatTime(timestamp)}
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/**
 * Format tool name for display.
 */
function formatToolName(tool: string): string {
  return tool
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Format timestamp for display.
 */
function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
