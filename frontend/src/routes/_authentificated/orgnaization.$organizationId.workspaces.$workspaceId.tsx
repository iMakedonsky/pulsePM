import { createFileRoute } from '@tanstack/react-router';
import { WorkItemsTable } from '#/components/workspaceContent/WorkItemsTable.tsx';
import { WorkspaceDashboard } from '#/components/workspaceContent/WorkspaceDashboard.tsx';

export const Route = createFileRoute('/_authentificated/orgnaization/$organizationId/workspaces/$workspaceId')({
  component: WorkspacePage,
});

function WorkspacePage() {
  const { organizationId, workspaceId } = Route.useParams();

  return (
    <main className="page-wrap py-16">
      {/*TODO: Implement the <Link> conponents as tabs or embed the Material-UI with router*/}
      <WorkspaceDashboard organizationId={organizationId} workspaceId={workspaceId} />
      <section className="island-shell rise-in mx-auto mt-10 max-w-5xl rounded-3xl">
        <WorkItemsTable organizationId={organizationId} workspaceId={workspaceId} />
      </section>
    </main>
  );
}
