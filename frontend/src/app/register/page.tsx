import { AuthForm } from "@/components/AuthForm";

/**
 * Registration page
 *
 * Server component that renders the registration form for new users.
 * After successful registration, users are redirected to /dashboard.
 */
export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-gray-50 dark:bg-gray-900">
      <main className="w-full">
        <AuthForm mode="register" />
      </main>
    </div>
  );
}
