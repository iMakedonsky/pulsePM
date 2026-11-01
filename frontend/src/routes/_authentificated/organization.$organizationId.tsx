import { useQuery } from '@tanstack/react-query';
import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';
import { InvitationForm } from '#/components/UI/InvitationForm.tsx';
import { ApiError, currentUserQueryKey, getListInvitations, getListWorkspaces, getOrganizationData } from '#/lib/auth-api.ts';

export const Route = createFileRoute('/_authentificated/organization/$organizationId')({
  component: OrganizationDashboard,
});

const INVITATION_STATUS: Record<string, string> = { null: 'Pending', true: 'Accepted', false: 'Rejected' };

function OrganizationDashboard() {
  const { organizationId } = Route.useParams();

  const [isInvitationFormVisible, setIsInvitationFormVisible] = useState<boolean>(false);
  const [isInvitationsCollapsed, setIsInvitationsCollapsed] = useState<boolean>(false);

  const organizationData = useQuery({
    queryKey: [...currentUserQueryKey, 'organization', organizationId],
    queryFn: () => getOrganizationData(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  const workspacesList = useQuery({
    queryKey: [...currentUserQueryKey, 'workspaces', organizationId],
    queryFn: () => getListWorkspaces(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  const invitationList = useQuery({
    queryKey: [...currentUserQueryKey, 'invitations', organizationId],
    queryFn: () => getListInvitations(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  if (organizationData.isLoading || organizationData.isPending) {
    return <main className="page-wrap py-16">Loading profile…</main>;
  }
  // handle the error status with an access/not-found state instead of silently returning.
  if (!organizationData.data) {
    return null;
  }

  const { owner, name, description } = organizationData.data;
  const listWorkspaces = workspacesList.data ?? [];
  const listInvitations = invitationList.data ?? [];
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
            <div className="flex flex-row items-center justify-between gap-[15px]">
              <h3 className="text-center">Organization table</h3>
              <button
                aria-label="Open registration form"
                type="button"
                className="mt-5 mb-5 cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
              >
                Collaps button
              </button>
            </div>
            <div className={`flex flex-row items-center justify-between gap-[15px]`}>
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
          </div>
        )}
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
        {invitationList.error instanceof ApiError ? (
          <div className="max-w-full content-center p-5 text-center">
            <p>Organization haven't created invitation yet!</p>
          </div>
        ) : (
          <div className="overflow-hidden rounded-3xl p-8">
            <hr className="mt-1 border-[var(--line)] border-t" />

            <div className="flex flex-row items-center justify-between gap-[15px]">
              <h3 className="text-center">Invitation table</h3>
              <button
                aria-label="Open registration form"
                type="button"
                className="mt-5 mb-5 cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
                onClick={() => setIsInvitationsCollapsed(!isInvitationsCollapsed)}
              >
                {isInvitationsCollapsed ? 'Collaps' : 'Uncollaspse'}
              </button>
            </div>
            <hr className="mt-1 border-[var(--line)] border-t" />
            <div
              className={`flex flex-row items-center justify-between gap-[15px] ${isInvitationsCollapsed ? 'hidden' : 'block'}`}
            >
              <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
                <thead>
                  <tr>
                    <th className="rounded-md border border-[var(--sea-ink)] p-2">Email</th>
                    <th className="rounded-md border border-[var(--sea-ink)] p-2">Sent by (member id)</th>
                    <th className="rounded-md border border-[var(--sea-ink)] p-2">Accepted</th>
                  </tr>
                </thead>
                <tbody className="w-full">
                  {listInvitations.map((invitation) => (
                    <tr key={invitation.id} className="border border-[var(--sea-ink)]">
                      <td className="p-2">{invitation.email}</td>
                      <td className="p-2">{invitation.sender_name}</td>
                      <td className="p-2">{INVITATION_STATUS[String(invitation.accepted)]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
