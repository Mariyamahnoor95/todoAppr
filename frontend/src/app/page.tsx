import { AuthForm } from "@/components/AuthForm";

/**
 * Home page - Login
 *
 * Server component that renders the login form for unauthenticated users.
 * After successful login, users are redirected to /dashboard.
 */
export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-gray-50 dark:bg-gray-900">
      <main className="w-full">
        <AuthForm mode="login" />
      </main>
    </div>
  );
}
