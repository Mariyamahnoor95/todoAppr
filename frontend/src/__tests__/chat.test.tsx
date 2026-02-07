/**
 * Tests for Chat components.
 *
 * Tests ChatMessage, ChatInput, and Chat components
 * for correct rendering and user interactions.
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { Chat } from "@/components/Chat";

// Mock the chat API
jest.mock("@/lib/chat-api", () => ({
  chatApi: {
    sendMessage: jest.fn(),
    getConversation: jest.fn(),
    listConversations: jest.fn(),
    deleteConversation: jest.fn(),
  },
}));

// Mock the API error class
jest.mock("@/lib/api", () => ({
  ApiError: class ApiError extends Error {
    constructor(public status: number, message: string) {
      super(message);
    }
  },
}));

describe("ChatMessage", () => {
  it("renders user message with correct styling", () => {
    render(
      <ChatMessage
        role="user"
        content="Hello, bot!"
        timestamp={new Date("2024-01-15T10:30:00")}
      />
    );

    expect(screen.getByText("Hello, bot!")).toBeInTheDocument();
    // User messages should be on the right (justify-end)
    const container = screen.getByText("Hello, bot!").closest("div[class*='justify-']");
    expect(container).toHaveClass("justify-end");
  });

  it("renders assistant message with correct styling", () => {
    render(
      <ChatMessage
        role="assistant"
        content="I can help you with that!"
        timestamp={new Date("2024-01-15T10:30:00")}
      />
    );

    expect(screen.getByText("I can help you with that!")).toBeInTheDocument();
    // Assistant messages should be on the left (justify-start)
    const container = screen.getByText("I can help you with that!").closest("div[class*='justify-']");
    expect(container).toHaveClass("justify-start");
  });

  it("shows loading indicator when isLoading is true", () => {
    render(
      <ChatMessage role="assistant" content="" isLoading={true} />
    );

    expect(screen.getByText("Thinking...")).toBeInTheDocument();
  });

  it("displays tool calls when present", () => {
    const toolCalls = [
      { tool: "add_task", result: { status: "created", task_id: "123" } },
    ];

    render(
      <ChatMessage
        role="assistant"
        content="I've added the task."
        toolCalls={toolCalls}
      />
    );

    expect(screen.getByText("Actions performed:")).toBeInTheDocument();
    expect(screen.getByText("Add Task")).toBeInTheDocument();
    expect(screen.getByText(/created/)).toBeInTheDocument();
  });

  it("formats timestamp correctly", () => {
    render(
      <ChatMessage
        role="user"
        content="Test message"
        timestamp={new Date("2024-01-15T14:30:00")}
      />
    );

    // Should show time in HH:MM format
    expect(screen.getByText(/\d{1,2}:\d{2}/)).toBeInTheDocument();
  });

  it("does not show tool calls section when empty", () => {
    render(
      <ChatMessage
        role="assistant"
        content="Just a regular message"
        toolCalls={[]}
      />
    );

    expect(screen.queryByText("Actions performed:")).not.toBeInTheDocument();
  });
});

describe("ChatInput", () => {
  it("renders input field with placeholder", () => {
    const onSend = jest.fn();
    render(<ChatInput onSend={onSend} placeholder="Type a message..." />);

    expect(screen.getByPlaceholderText("Type a message...")).toBeInTheDocument();
  });

  it("calls onSend when form is submitted", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Hello!");

    const button = screen.getByRole("button");
    await user.click(button);

    expect(onSend).toHaveBeenCalledWith("Hello!");
  });

  it("calls onSend when Enter is pressed", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Hello!{Enter}");

    expect(onSend).toHaveBeenCalledWith("Hello!");
  });

  it("does not submit on Shift+Enter", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Hello!{Shift>}{Enter}{/Shift}");

    expect(onSend).not.toHaveBeenCalled();
  });

  it("clears input after sending", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Hello!");

    const button = screen.getByRole("button");
    await user.click(button);

    expect(input).toHaveValue("");
  });

  it("disables input when disabled prop is true", () => {
    const onSend = jest.fn();
    render(<ChatInput onSend={onSend} disabled={true} />);

    expect(screen.getByRole("textbox")).toBeDisabled();
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("does not send empty messages", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const button = screen.getByRole("button");
    await user.click(button);

    expect(onSend).not.toHaveBeenCalled();
  });

  it("trims whitespace from messages", async () => {
    const onSend = jest.fn();
    const user = userEvent.setup();

    render(<ChatInput onSend={onSend} />);

    const input = screen.getByRole("textbox");
    await user.type(input, "  Hello!  ");

    const button = screen.getByRole("button");
    await user.click(button);

    expect(onSend).toHaveBeenCalledWith("Hello!");
  });
});

describe("Chat", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders empty state with suggestions", () => {
    render(<Chat />);

    expect(screen.getByText("Task Assistant")).toBeInTheDocument();
    expect(screen.getByText(/I'm your Task Assistant/)).toBeInTheDocument();
    expect(screen.getByText(/Add a task to buy groceries/)).toBeInTheDocument();
    expect(screen.getByText(/Show me all my tasks/)).toBeInTheDocument();
  });

  it("renders chat header with New Chat button", () => {
    render(<Chat />);

    expect(screen.getByText("Task Assistant")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /new chat/i })).toBeInTheDocument();
  });

  it("renders input field", () => {
    render(<Chat />);

    expect(
      screen.getByPlaceholderText("Ask me to manage your tasks...")
    ).toBeInTheDocument();
  });

  it("New Chat button is disabled when no messages", () => {
    render(<Chat />);

    const newChatButton = screen.getByRole("button", { name: /new chat/i });
    expect(newChatButton).toBeDisabled();
  });
});

describe("Chat integration", () => {
  const { chatApi } = require("@/lib/chat-api");

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("sends message and displays response", async () => {
    chatApi.sendMessage.mockResolvedValueOnce({
      conversation_id: "conv-123",
      response: "I've added 'Buy groceries' to your tasks.",
      tool_calls: [{ tool: "add_task", result: { status: "created" } }],
    });

    const user = userEvent.setup();
    render(<Chat />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Add a task to buy groceries");

    const button = screen.getByRole("button", { name: /send/i });
    await user.click(button);

    // User message should appear
    await waitFor(() => {
      expect(screen.getByText("Add a task to buy groceries")).toBeInTheDocument();
    });

    // Assistant response should appear
    await waitFor(() => {
      expect(
        screen.getByText("I've added 'Buy groceries' to your tasks.")
      ).toBeInTheDocument();
    });
  });

  it("shows loading state while waiting for response", async () => {
    // Make the API call hang
    chatApi.sendMessage.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    );

    const user = userEvent.setup();
    render(<Chat />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Test message");

    const button = screen.getByRole("button", { name: /send/i });
    await user.click(button);

    // Loading indicator should appear
    await waitFor(() => {
      expect(screen.getByText("Thinking...")).toBeInTheDocument();
    });
  });

  it("displays error when API call fails", async () => {
    const { ApiError } = require("@/lib/api");
    chatApi.sendMessage.mockRejectedValueOnce(
      new ApiError(500, "Server error")
    );

    const user = userEvent.setup();
    render(<Chat />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Test message");

    const button = screen.getByRole("button", { name: /send/i });
    await user.click(button);

    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText("Server error")).toBeInTheDocument();
    });
  });

  it("clears messages when New Chat is clicked", async () => {
    chatApi.sendMessage.mockResolvedValueOnce({
      conversation_id: "conv-123",
      response: "Hello!",
      tool_calls: [],
    });

    const user = userEvent.setup();
    render(<Chat />);

    // Send a message first
    const input = screen.getByRole("textbox");
    await user.type(input, "Hi");
    const sendButton = screen.getByRole("button", { name: /send/i });
    await user.click(sendButton);

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText("Hello!")).toBeInTheDocument();
    });

    // New Chat button should now be enabled
    const newChatButton = screen.getByRole("button", { name: /new chat/i });
    expect(newChatButton).not.toBeDisabled();

    // Click New Chat
    await user.click(newChatButton);

    // Messages should be cleared, empty state should show
    await waitFor(() => {
      expect(screen.getByText(/I'm your Task Assistant/)).toBeInTheDocument();
    });
  });
});
