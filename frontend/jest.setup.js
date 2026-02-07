/**
 * Jest setup file for React Testing Library.
 */

import "@testing-library/jest-dom";

// Mock scrollIntoView (not available in jsdom)
Element.prototype.scrollIntoView = jest.fn();

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock zustand stores
jest.mock("@/lib/store", () => ({
  useAuthStore: {
    getState: () => ({
      user: { id: "test-user-123", email: "test@example.com" },
      token: "test-token",
      isAuthenticated: true,
    }),
  },
  useTaskStore: {
    getState: () => ({
      tasks: [],
      isLoading: false,
      error: null,
    }),
  },
}));
