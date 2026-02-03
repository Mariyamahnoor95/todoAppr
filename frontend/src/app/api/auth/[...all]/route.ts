/**
 * Better Auth API route handler.
 *
 * Handles all authentication requests (/api/auth/*).
 * Better Auth automatically creates endpoints for:
 * - POST /api/auth/sign-up/email (register)
 * - POST /api/auth/sign-in/email (login)
 * - POST /api/auth/sign-out (logout)
 * - GET /api/auth/get-session (get current session)
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
