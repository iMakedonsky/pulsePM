import { useQuery } from '@tanstack/react-query';
import { currentUserQueryKey } from '#/lib/authApi.ts';
import { getWorkspace } from '#/lib/workspaceApi.ts';

export function WorkspaceDashboard({ organizationId, workspaceId }: { organizationId: string; workspaceId: string }) {
  const getWorkspaceData = useQuery({
    queryKey: [...currentUserQueryKey, 'workspace', workspaceId],
    queryFn: () => getWorkspace(Number(organizationId), Number(workspaceId)),
    enabled: true,
    retry: false,
  });

  if (getWorkspaceData.isError) {
    return <p className="text-red-600">Failed to load workspace.</p>;
  }

  if (getWorkspaceData.isPending || getWorkspaceData.isLoading) {
    return <p className="text-[var(--sea-ink-soft)]">Loading workspace...</p>;
  }

  return (
    <section className="island-shell rise-in mx-auto max-w-2xl rounded-3xl p-8 text-center">
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
            <p className="mt-2 text-[var(--sea-ink-soft)]">
              {getWorkspaceData.data.description ? getWorkspaceData.data.description : '-'}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
