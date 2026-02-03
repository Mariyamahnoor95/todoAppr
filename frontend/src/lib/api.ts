/**
 * API client for backend communication.
 *
 * Provides type-safe methods for interacting with the FastAPI backend.
 * Handles authentication tokens, error responses, and request formatting.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Base fetch wrapper with error handling and JSON parsing.
 *
 * @param endpoint - API endpoint path (e.g., "/api/{userId}/tasks")
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws ApiError on HTTP error responses
 */
async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  // Get the JWT token from Zustand auth store
  const { useAuthStore } = await import("@/lib/store");
  const token = useAuthStore.getState().token;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add Authorization header with JWT token
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// TypeScript types for API responses
export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface MessageResponse {
  message: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  skip: number;
  limit: number;
}

export interface TaskCreateRequest {
  title: string;
  description?: string | null;
}

export interface TaskUpdateRequest {
  title?: string | null;
  description?: string | null;
  completed?: boolean | null;
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
 * Task API methods
 *
 * All endpoints use /api/{user_id}/tasks format.
 * JWT token is sent in Authorization header, and
 * user_id in the URL is verified against the JWT on the backend.
 */
export const taskApi = {
  list: async (params?: {
    skip?: number;
    limit?: number;
    completed?: boolean;
  }): Promise<TaskListResponse> => {
    const userId = await getUserId();
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append("skip", params.skip.toString());
    if (params?.limit !== undefined) queryParams.append("limit", params.limit.toString());
    if (params?.completed !== undefined)
      queryParams.append("completed", params.completed.toString());

    const query = queryParams.toString();
    return fetchApi<TaskListResponse>(`/api/${userId}/tasks${query ? `?${query}` : ""}`);
  },

  get: async (id: string): Promise<Task> => {
    const userId = await getUserId();
    return fetchApi<Task>(`/api/${userId}/tasks/${id}`);
  },

  create: async (data: TaskCreateRequest): Promise<Task> => {
    const userId = await getUserId();
    return fetchApi<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update: async (id: string, data: TaskUpdateRequest): Promise<Task> => {
    const userId = await getUserId();
    return fetchApi<Task>(`/api/${userId}/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  toggle: async (id: string): Promise<Task> => {
    const userId = await getUserId();
    return fetchApi<Task>(`/api/${userId}/tasks/${id}/complete`, {
      method: "PATCH",
    });
  },

  delete: async (id: string): Promise<MessageResponse> => {
    const userId = await getUserId();
    return fetchApi<MessageResponse>(`/api/${userId}/tasks/${id}`, {
      method: "DELETE",
    });
  },
};

export { fetchApi };
