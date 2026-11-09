import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { currentUserQueryKey } from '#/lib/authApi.ts';
import { getListWorkitems } from '#/lib/workspaceApi.ts';

export function WorkItemsTable({ organizationId, workspaceId }: { organizationId: string; workspaceId: string }) {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);

  const getWorkItemsData = useQuery({
    queryKey: [...currentUserQueryKey, 'workItems', organizationId, workspaceId],
    queryFn: () => getListWorkitems(Number(organizationId), Number(workspaceId)),
    enabled: true,
    retry: false,
  });

  if (getWorkItemsData.isError) {
    return (
      <div className="max-w-full content-center p-5 text-center">
        <p className="text-red-600">Failed to load work items.</p>
      </div>
    );
  }

  if (getWorkItemsData.isPending || getWorkItemsData.isLoading) {
    return <p className="text-[var(--sea-ink-soft)]">Loading work items...</p>;
  }

  const headerCell = 'rounded-md border border-[var(--sea-ink)] p-2';

  return (
    <div className="rounded-3xl p-8">
      <div className="flex flex-row items-center justify-between gap-[15px]">
        <h3 className="text-center">Work items</h3>
        <button
          aria-label="Toggle work items table"
          type="button"
          className="mt-5 mb-5 cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? 'Uncollapse' : 'Collapse'}
        </button>
      </div>
      <div className={`block overflow-x-scroll ${isCollapsed ? `hidden` : `block`}`}>
        {getWorkItemsData.data?.length === 0 ? (
          <p className="p-5 text-center text-[var(--sea-ink-soft)]">No work items yet.</p>
        ) : (
          <table className="w-full p-2 text-center">
            <thead className="">
              <tr>
                <th className={headerCell}>ID</th>
                <th className={headerCell}>Title</th>
                <th className={headerCell}>Assigned to</th>
                <th className={headerCell}>Status</th>
                <th className={headerCell}>Priority</th>
                <th className={headerCell}>Created</th>
                <th className={headerCell}>Due</th>
                <th className={headerCell}>Last modified by</th>
              </tr>
            </thead>
            <tbody className="w-full">
              {getWorkItemsData.data?.map((item) => (
                <tr key={item.id} className="border border-[var(--sea-ink)] hover:bg-[var(--sand)]">
                  <td className="p-2">{item.id}</td>
                  <td className="truncate p-2">{item.title}</td>
                  <td className="p-2">{item.assignee_name}</td>
                  <td className="p-2">{item.status}</td>
                  <td className="p-2">{item.priority}</td>
                  <td className="p-2">{new Date(item.created_at).toLocaleDateString()}</td>
                  <td className="p-2">{item.due_date ? new Date(item.due_date).toLocaleDateString() : '—'}</td>
                  <td className="truncate p-2">{new Date(item.last_update).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
