/**
 * Better Auth configuration.
 *
 * Handles authentication with Neon PostgreSQL database.
 * Issues JWT tokens that can be validated by the FastAPI backend.
 */

import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d", // 7 days
      },
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
