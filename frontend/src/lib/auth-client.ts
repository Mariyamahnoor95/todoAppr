/**
 * Better Auth client for frontend.
 *
 * Provides methods to interact with Better Auth API.
 * Uses JWT plugin to get JWT tokens for backend API authentication.
 */

import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient;
