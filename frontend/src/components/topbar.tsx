import { Link } from '@tanstack/react-router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { getCurrentUser, login, logout } from '../lib/auth-api';

export const currentUserQueryKey = ['auth', 'me'] as const;

export function Topbar() {
  const queryClient = useQueryClient();
  const currentUser = useQuery({
    queryKey: currentUserQueryKey,
    queryFn: getCurrentUser,
    enabled: typeof window !== 'undefined',
    retry: false,
  });
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const loginMutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: (user) => {
      queryClient.setQueryData(currentUserQueryKey, user);
      setPassword('');
    },
  });
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () =>
      queryClient.removeQueries({ queryKey: currentUserQueryKey }),
  });

  return (
    <header className="border-b border-[var(--line)] bg-[var(--header-bg)]">
      <div className="page-wrap flex min-h-16 items-center justify-between gap-4 py-3">
        <Link
          to="/"
          className="display-title text-xl font-bold no-underline text-[var(--sea-ink)]"
        >
          PulsePM
        </Link>
        {currentUser.data ? (
          <div className="flex items-center gap-4 text-sm">
            <Link to="/profile" className="nav-link">
              {currentUser.data.first_name || currentUser.data.email}
            </Link>
            <button
              type="button"
              className="rounded-md bg-[var(--sea-ink)] px-3 py-2 text-white"
              onClick={() => logoutMutation.mutate()}
            >
              {logoutMutation.isPending ? 'Signing out…' : 'Logout'}
            </button>
          </div>
        ) : (
          <form
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
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Email"
              required
            />
            <input
              aria-label="Password"
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              required
            />
            <button
              type="submit"
              className="rounded-md bg-[var(--lagoon-deep)] px-3 py-2 text-sm font-semibold text-white"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? 'Signing in…' : 'Login'}
            </button>
            {loginMutation.isError ? (
              <span className="text-xs text-red-700">
                {loginMutation.error.message}
              </span>
            ) : null}
          </form>
        )}
      </div>
    </header>
  );
}
