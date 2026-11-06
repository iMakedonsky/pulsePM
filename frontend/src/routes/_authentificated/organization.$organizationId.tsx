import { useQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { InvitationForm } from '#/components/UI/InvitationForm.tsx';
import { InvitationLists } from '#/components/UI/InvitationLists.tsx';
import { WorkspaceLists } from '#/components/UI/WorkspaceLists.tsx';
import { ApiError, currentUserQueryKey, getOrganizationData } from '#/lib/auth-api.ts';

export const Route = createFileRoute('/_authentificated/organization/$organizationId')({
  component: OrganizationDashboard,
});

function OrganizationDashboard() {
  const { organizationId } = Route.useParams();

  const [isInvitationFormVisible, setIsInvitationFormVisible] = useState<boolean>(false);

  const organizationData = useQuery({
    queryKey: [...currentUserQueryKey, 'organization', organizationId],
    queryFn: () => getOrganizationData(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  if (organizationData.isLoading || organizationData.isPending) {
    return <main className="page-wrap py-16">Organization details…</main>;
  }

  if (organizationData.error instanceof ApiError) {
    return <main className="page-wrap py-16 text-4xl">{organizationData.error.message}</main>;
  }

  return (
    <main className="page-wrap py-16">
      <section className="island-shell rise-in mx-auto max-w-2xl rounded-3xl p-8 text-center">
        <div className="flex flex-col items-center gap-6">
          <div>
            <p className="island-kicker">Organization</p>
            <h1 className="display-title mt-3 font-bold text-[32px]">{organizationData.data?.name}</h1>
            <hr className="mx-auto mt-4 w-16 border-[var(--line)] border-t" />
            <p className="island-kicker mt-6">Owner</p>
            <h2 className="display-title mt-2 font-semibold text-lg">{organizationData.data?.owner_name}</h2>
          </div>
          <div>
            <p className="island-kicker">Description</p>
            <p className="mt-2 text-[var(--sea-ink-soft)]">{organizationData.data?.description}</p>
          </div>
        </div>
      </section>
      <section className="island-shell rise-in mx-auto mt-10 max-w-5xl rounded-3xl">
        <WorkspaceLists organizationId={organizationId} />
        <hr className="mt-1 border-[var(--line)] border-t" />
        <div className="flex flex-col gap-6">
          <h3 className="display-title text-center font-semibold text-lg">Invitations</h3>
          <div className="flex flex-row items-center gap-[15px] pl-15.5">
            <button
              aria-label="Open registration form"
              type="button"
              className="cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
              onClick={() => setIsInvitationFormVisible(true)}
            >
              Create invitation
            </button>
            <div>
              <p className="text-[var(--sea-ink-soft)] italic">
                Invite people to join your organization and collaborate with the team.
              </p>
            </div>
          </div>
        </div>
        <InvitationForm
          organizationId={Number(organizationId)}
          isInvitationFormVisible={isInvitationFormVisible}
          onClose={() => setIsInvitationFormVisible(false)}
        />
        <InvitationLists organizationId={organizationId} />
      </section>
    </main>
  );
}
