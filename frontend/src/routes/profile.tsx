import { useQuery } from '@tanstack/react-query';

import { ApiError, currentUserQueryKey, getCurrentUser } from '../lib/auth-api';

export const Route = createFileRoute('/profile')({ component: Profile });

function Profile() {
  const currentUser = useQuery({
    queryKey: currentUserQueryKey,
    queryFn: getCurrentUser,
    enabled: typeof window !== 'undefined',
    retry: false,
  });

  if (currentUser.isLoading || currentUser.isPending) {
    return <main className="page-wrap py-16">Loading profile…</main>;
  }
  if (currentUser.error instanceof ApiError && currentUser.error.status === 401) {
    return (
      <main className="page-wrap py-16">
        <section className="island-shell rounded-2xl p-8">
          <h1 className="display-title font-bold text-3xl">Profile locked</h1>
          <p className="mt-3">Please log in from the top bar to access your profile.</p>
          <Link to="/" className="mt-5 inline-block">
            Return home
          </Link>
        </section>
      </main>
    );
  }
  if (!currentUser.data) {
    return null;
  }

  const { first_name, last_name, email, id } = currentUser.data;
  return (
    <main className="page-wrap py-16">
      <section className="island-shell rise-in max-w-2xl rounded-3xl p-8">
        <p className="island-kicker">Your account</p>
        <h1 className="display-title mt-3 font-bold text-4xl">
          {[first_name, last_name].filter(Boolean).join(' ') || 'Profile'}
        </h1>
        <dl className="mt-8 grid gap-5 text-sm">
          <div>
            <dt className="font-semibold text-[var(--sea-ink-soft)]">Email</dt>
            <dd className="mt-1 text-lg">{email}</dd>
          </div>
          <div>
            <dt className="font-semibold text-[var(--sea-ink-soft)]">Member ID</dt>
            <dd className="mt-1 text-lg">{id}</dd>
          </div>
        </dl>
      </section>
    </main>
  );
}
