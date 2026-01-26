"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { authApi, ApiError } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

/**
 * Authentication hook for managing user authentication state.
 *
 * Provides methods for login, register, logout and accessing current user.
 * Automatically syncs with Zustand store and handles routing.
 *
 * @example
 * ```tsx
 * function LoginPage() {
 *   const { login, isLoading, error, user } = useAuth();
 *
 *   const handleLogin = async () => {
 *     await login("user@example.com", "password");
 *   };
 *
 *   return <button onClick={handleLogin}>Login</button>;
 * }
 * ```
 */
export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, setUser, logout: clearUser } = useAuthStore();

  /**
   * Check if user is authenticated on mount
   */
  useEffect(() => {
    const checkAuth = async () => {
      if (!user) {
        try {
          const currentUser = await authApi.me();
          setUser(currentUser);
        } catch (error) {
          // Not authenticated, clear any stale state
          clearUser();
        }
      }
    };

    checkAuth();
  }, [user, setUser, clearUser]);

  /**
   * Register a new user account
   * @param email - User's email address
   * @param password - User's password
   * @throws ApiError if registration fails
   */
  const register = async (email: string, password: string): Promise<void> => {
    try {
      const response = await authApi.register(email, password);
      setUser(response.user);
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new Error("Registration failed");
    }
  };

  /**
   * Login with email and password
   * @param email - User's email address
   * @param password - User's password
   * @throws ApiError if login fails
   */
  const login = async (email: string, password: string): Promise<void> => {
    try {
      const response = await authApi.login(email, password);
      setUser(response.user);
      router.push("/dashboard");
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new Error("Login failed");
    }
  };

  /**
   * Logout current user and redirect to login page
   */
  const logout = async (): Promise<void> => {
    try {
      await authApi.logout();
      clearUser();
      router.push("/");
    } catch (error) {
      // Clear local state even if API call fails
      clearUser();
      router.push("/");
    }
  };

  return {
    user,
    isAuthenticated,
    register,
    login,
    logout,
  };
}
