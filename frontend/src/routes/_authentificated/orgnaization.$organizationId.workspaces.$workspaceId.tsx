import { useQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { currentUserQueryKey } from '#/lib/authApi.ts';
import { getWorkspace } from '#/lib/workspaceApi.ts';

export const Route = createFileRoute('/_authentificated/orgnaization/$organizationId/workspaces/$workspaceId')({
  component: WorkspaceDashboard,
});

function WorkspaceDashboard() {
  const { organizationId, workspaceId } = Route.useParams();
  const getWorkspaceData = useQuery({
    queryKey: [...currentUserQueryKey, 'workspace', workspaceId],
    queryFn: () => getWorkspace(Number(organizationId), Number(workspaceId)),
    enabled: true,
    retry: false,
  });

  return (
    <main className="page-wrap py-16">
      <section className="island-shell rise-in mx-auto max-w-2xl rounded-3xl p-8 text-center">
        {getWorkspaceData.isPending && <p className="text-[var(--sea-ink-soft)]">Loading workspace...</p>}
        {getWorkspaceData.isError && <p className="text-red-600">Failed to load workspace.</p>}
        {getWorkspaceData.data && (
          <div className="flex flex-col items-center gap-6">
            <div>
              {getWorkspaceData.data.icon_url && (
                <img
                  src={getWorkspaceData.data.icon_url}
                  alt={`${getWorkspaceData.data.name} icon`}
                  className="mx-auto mb-4 h-16 w-16 rounded-2xl object-cover"
                />
              )}
              <p className="island-kicker">Workspace</p>
              <h1 className="display-title mt-3 font-bold text-[32px]">{getWorkspaceData.data.name}</h1>
              <hr className="mx-auto mt-4 w-16 border-[var(--line)] border-t" />
              <p className="island-kicker mt-6">Space code</p>
              <h2 className="display-title mt-2 font-semibold text-lg">{getWorkspaceData.data.space_code}</h2>
            </div>
            <div>
              <p className="island-kicker">Description</p>
              <p className="mt-2 text-[var(--sea-ink-soft)]">{getWorkspaceData.data.description}</p>
            </div>
          </div>
        )}
      </section>
      <section className="island-shell rise-in mx-auto mt-10 max-w-5xl rounded-3xl">
        <hr className="mt-1 border-[var(--line)] border-t" />
        <div className="flex flex-col gap-6">
          <h3 className="display-title text-center font-semibold text-lg">Invitations</h3>
          <div className="flex flex-row items-center gap-[15px] pl-15.5">
            <div>
              <p className="text-[var(--sea-ink-soft)] italic">
                Invite people to join your organization and collaborate with the team.
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
