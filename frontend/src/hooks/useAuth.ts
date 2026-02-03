"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { useAuthStore } from "@/lib/store";
import { ApiError } from "@/lib/api";

/**
 * Authentication hook for managing user authentication state.
 *
 * Provides methods for login, register, logout and accessing current user.
 * Automatically syncs with Zustand store and handles routing.
 * Now uses Better Auth for authentication.
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
  const { user, isAuthenticated, setUser, setToken, logout: clearUser } = useAuthStore();

  /**
   * Fetch JWT token from Better Auth and store it
   */
  const fetchAndStoreToken = async () => {
    try {
      const { data } = await authClient.token();
      if (data?.token) {
        setToken(data.token);
      }
    } catch {
      // Token fetch failed, will retry on next request
    }
  };

  /**
   * Check if user is authenticated on mount using Better Auth session
   */
  useEffect(() => {
    const checkAuth = async () => {
      if (!user) {
        try {
          const { data: session } = await authClient.getSession();
          if (session?.user) {
            setUser({
              id: session.user.id,
              email: session.user.email,
              created_at: session.user.createdAt,
            });
            // Fetch JWT token for backend API calls
            await fetchAndStoreToken();
          } else {
            clearUser();
          }
        } catch {
          clearUser();
        }
      }
    };

    checkAuth();
  }, [user, setUser, clearUser]);

  /**
   * Register a new user account using Better Auth
   */
  const register = async (email: string, password: string): Promise<void> => {
    try {
      const { data, error } = await authClient.signUp.email({
        email,
        password,
        name: email.split("@")[0],
      });

      if (error) {
        throw new ApiError(400, error.message || "Registration failed");
      }

      if (data?.user) {
        setUser({
          id: data.user.id,
          email: data.user.email,
          created_at: data.user.createdAt,
        });
        // Fetch JWT token for backend API calls
        await fetchAndStoreToken();
        router.push("/dashboard");
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new Error("Registration failed");
    }
  };

  /**
   * Login with email and password using Better Auth
   */
  const login = async (email: string, password: string): Promise<void> => {
    try {
      const { data, error } = await authClient.signIn.email({
        email,
        password,
      });

      if (error) {
        throw new ApiError(401, error.message || "Login failed");
      }

      if (data?.user) {
        setUser({
          id: data.user.id,
          email: data.user.email,
          created_at: data.user.createdAt,
        });
        // Fetch JWT token for backend API calls
        await fetchAndStoreToken();
        router.push("/dashboard");
      }
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
      await authClient.signOut();
      clearUser();
      router.push("/");
    } catch {
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
