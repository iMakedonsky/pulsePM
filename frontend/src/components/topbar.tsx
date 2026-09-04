import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { useId, useState } from 'react';
import { RegistrationModal } from '../components/UI/RegistrationModal.tsx';
import { useToast } from '../context/toast-context.ts';
import { currentUserQueryKey, getCurrentUser, login, logout } from '../lib/auth-api';

export function Topbar() {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const currentUser = useQuery({
    queryKey: currentUserQueryKey,
    queryFn: getCurrentUser,
    enabled: typeof window !== 'undefined',
    retry: false,
  });

  const [isRegistrationFormVisible, setIsRegistrationFormVisible] = useState<boolean>(false);

  const loginFormId = useId();
  const [LoginEmail, setLoginEmail] = useState<string>('');
  const [LoginPassword, setLoginPassword] = useState<string>('');
  const loginMutation = useMutation({
    mutationFn: () => login(LoginEmail, LoginPassword),
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user);
      setLoginPassword('');
      setIsRegistrationFormVisible(false);
      addToast(`${user.first_name ? user.first_name : 'user'} was logged in!`, 'Success');
    },
    onError: (error) => {
      addToast(error.message, 'Error');
    },
  });
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => queryClient.removeQueries({ queryKey: currentUserQueryKey }),
  });

  return (
    <header className="border-[var(--line)] border-b bg-[var(--header-bg)]">
      <div className="page-wrap flex min-h-16 items-center justify-between gap-4 py-3">
        <Link to="/" className="display-title font-bold text-[var(--sea-ink)] text-xl no-underline">
          PulsePM
        </Link>
        {currentUser.data ? (
          <div className="flex items-center gap-4 text-sm">
            <Link to="/profile" className="nav-link">
              {currentUser.data.first_name || currentUser.data.email}
            </Link>
            <button
              aria-label="Log out"
              type="button"
              className="rounded-md bg-[var(--sea-ink)] px-3 py-2 text-white"
              onClick={() => logoutMutation.mutate()}
            >
              {logoutMutation.isPending ? 'Signing out…' : 'Logout'}
            </button>
          </div>
        ) : (
          <form
            id={loginFormId}
            name="login"
            className="flex flex-wrap items-center justify-end gap-2"
            onSubmit={(event) => {
              event.preventDefault();
              loginMutation.mutate();
            }}
          >
            <input
              aria-label="Email"
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="email"
              value={LoginEmail}
              onChange={(event) => setLoginEmail(event.target.value)}
              placeholder="Email"
              required
            />
            <input
              aria-label="Password"
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="password"
              value={LoginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              placeholder="Password"
              required
            />
            <button
              aria-label="Log in"
              type="submit"
              className="cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? 'Signing in…' : 'Login'}
            </button>
            <button
              aria-label="Open registration form"
              type="button"
              className="cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
              onClick={() => setIsRegistrationFormVisible(true)}
              disabled={loginMutation.isPending}
            >
              Sign Up
            </button>
          </form>
        )}
        <RegistrationModal
          isRegistrationFormVisible={isRegistrationFormVisible}
          onClose={() => setIsRegistrationFormVisible(false)}
        />
      </div>
    </header>
  );
}
