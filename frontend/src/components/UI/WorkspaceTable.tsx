import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { currentUserQueryKey } from '#/lib/authApi.ts';
import { getListWorkspaces } from '#/lib/organizationApi.ts';

export function WorkspaceTable({ organizationId }: { organizationId: string }) {
  const [isWorkspacesCollapsed, setIsWorkspacesCollapsed] = useState<boolean>(false);

  const workspacesList = useQuery({
    queryKey: [...currentUserQueryKey, 'workspaces', organizationId],
    queryFn: () => getListWorkspaces(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  if (workspacesList.isError) {
    return (
      <div className="max-w-full content-center p-5 text-center">
        <p>Organization haven't created workspace yet!</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-3xl p-8">
      <div className="flex flex-row items-center justify-between gap-[15px]">
        <h3 className="text-center">Workspaces table</h3>
        <button
          aria-label="Open registration form"
          type="button"
          className="mt-5 mb-5 cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
          onClick={() => {
            setIsWorkspacesCollapsed(!isWorkspacesCollapsed);
          }}
        >
          {isWorkspacesCollapsed ? 'Collaps' : 'Uncollaspse'}
        </button>
      </div>
      <div className={`flex flex-row items-center justify-between gap-[15px] ${isWorkspacesCollapsed ? 'hidden' : 'block'}`}>
        <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
          <thead>
            <tr>
              <th className="rounded-md border border-[var(--sea-ink)] p-2">Name</th>
              <th className="rounded-md border border-[var(--sea-ink)] p-2">Space code</th>
            </tr>
          </thead>
          <tbody className="w-full">
            {workspacesList.data?.map((workspace) => (
              <tr key={workspace.id} className="relative border border-[var(--sea-ink)] hover:bg-[var(--sand)]">
                <td className="p-2">
                  <Link
                    to={`/orgnaization/$organizationId/workspaces/$workspaceId`}
                    params={{ organizationId, workspaceId: String(workspace.id) }}
                    className="after:absolute after:inset-0"
                  >
                    {workspace.name}
                  </Link>
                </td>
                <td className="p-2">{workspace.space_code}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
