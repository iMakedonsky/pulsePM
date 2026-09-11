import { useQuery } from '@tanstack/react-query';
import { createFileRoute, Link } from '@tanstack/react-router';
import { ApiError, currentUserQueryKey, getListWorkspaces, getOrganizationData } from '#/lib/auth-api.ts';

export const Route = createFileRoute('/organization/$organizationId')({
  component: OrganizationDashboard,
});

function OrganizationDashboard() {
  const { organizationId } = Route.useParams();

  const organizationData = useQuery({
    queryKey: [...currentUserQueryKey, 'organization', organizationId],
    queryFn: () => getOrganizationData(Number(organizationId)),
    enabled: typeof window !== 'undefined',
    retry: false,
  });

  const workspacesList = useQuery({
    queryKey: [...currentUserQueryKey, 'workspaces', organizationId],
    queryFn: () => getListWorkspaces(Number(organizationId)),
    enabled: typeof window !== 'undefined',
    retry: false,
  });

  if (organizationData.isLoading || organizationData.isPending) {
    return <main className="page-wrap py-16">Loading profile…</main>;
  }
  if (organizationData.error instanceof ApiError && organizationData.error.status === 401) {
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
  if (!organizationData.data) {
    return null;
  }

  const { owner, name, description } = organizationData.data;
  const listWorkspaces = workspacesList.data ?? [];
  return (
    <main className="page-wrap py-16">
      <section className="island-shell rise-in mx-auto max-w-2xl rounded-3xl p-8 text-center">
        <div className="flex flex-col items-center gap-6">
          <div>
            <p className="island-kicker">Organization</p>
            <h1 className="display-title mt-3 font-bold text-[32px]">{name}</h1>
            <hr className="mx-auto mt-4 w-16 border-[var(--line)] border-t" />
            <p className="island-kicker mt-6">Owner</p>
            <h2 className="display-title mt-2 font-semibold text-lg">{owner}</h2>
          </div>
          <div>
            <p className="island-kicker">Description</p>
            <p className="mt-2 text-[var(--sea-ink-soft)]">{description}</p>
          </div>
        </div>
      </section>
      <section className="island-shell rise-in mx-auto mt-10 max-w-5xl rounded-3xl">
        {workspacesList.error instanceof ApiError && workspacesList.error.status === 404 ? (
          <div className="max-w-full content-center p-5 text-center">
            <p>Organization haven't created workspace yet!</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl p-8">
            <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
              <thead>
                <tr>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Name</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Space code</th>
                  <th className="rounded-md border border-[var(--sea-ink)] p-2">Created by</th>
                </tr>
              </thead>
              <tbody className="w-full">
                {listWorkspaces.map((workspace) => (
                  <tr key={workspace.id} className="relative border border-[var(--sea-ink)] hover:bg-[var(--sand)]">
                    <td className="p-2">
                      <Link to="/" className="after:absolute after:inset-0">
                        {workspace.name}
                      </Link>
                    </td>
                    <td className="p-2">{workspace.space_code}</td>
                    <td className="p-2">{workspace.created_by}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
