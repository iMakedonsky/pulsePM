import { useQuery } from '@tanstack/react-query';
import { createFileRoute, Link } from '@tanstack/react-router';

import { ApiError, currentUserQueryKey, getCurrentUser, getUserMemberShip } from '../lib/auth-api';

export const Route = createFileRoute('/profile')({ component: Profile });

function Profile() {
  const currentUser = useQuery({
    queryKey: currentUserQueryKey,
    queryFn: getCurrentUser,
    enabled: typeof window !== 'undefined',
    retry: false,
  });

  // TODO: Consider how better to rewrite userMemberShip, the reason is 'enabled'
  const userMemberShip = useQuery({
    queryKey: [...currentUserQueryKey, 'membership'],
    queryFn: getUserMemberShip,
    enabled: !!currentUser.data, // don't fire until authenticated
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
  // If the 'data' variable returns an underfind, it will be an empty array. This is to avoid a type error.
  const listMembership = userMemberShip.data ?? [];

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
      <section className="island-shell rise-in mt-10 max-w-5xl rounded-3xl">
        {userMemberShip.error instanceof ApiError && userMemberShip.error.status === 404 ? (
          <div className="max-w-full content-center p-5 align-center">
            <p>User haven't participated in any organizations yet!</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-t-3xl rounded-r-5xl rounded-b-3xl rounded-l-5xl">
            <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
              <thead>
                <tr>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">ID</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Name</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Role</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Position</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Last activity</th>
                </tr>
              </thead>
              <tbody className="w-full">
                {listMembership.map((member) => (
                  <tr key={member.id} className="relative border border-[var(--sea-ink)] hover:bg-[var(--sand)]">
                    <td className="p-2">
                      <Link
                        to={`/organization/$organizationId`}
                        params={{ organizationId: String(member.organization.id) }}
                        className="after:absolute after:inset-0"
                      >
                        {member.organization.id}
                      </Link>
                    </td>
                    <td className="p-2">{member.organization.name}</td>
                    <td className="p-2">{member.position}</td>
                    <td className="p-2">{member.role}</td>
                    <td className="p-2">{member.last_activity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <section className="island-shell rise-in mt-5 max-w-5xl rounded-3xl">
        {userMemberShip.error instanceof ApiError && userMemberShip.error.status === 404 ? (
          <div className="max-w-full content-center p-5 align-center">
            <p>User doesn't have any invitations!</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-t-3xl rounded-r-5xl rounded-b-3xl rounded-l-5xl">
            <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
              <thead>
                <tr>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">ID</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">link</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">date</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">status</th>
                </tr>
              </thead>
              <tbody className="w-full" />
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
