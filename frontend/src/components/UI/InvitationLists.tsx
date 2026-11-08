import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { ApiError } from '#/lib/apiClient.ts';
import { currentUserQueryKey } from '#/lib/authApi.ts';
import { getListInvitations } from '#/lib/organizationApi.ts';

interface InvitationStatus {
  label: string;
  color: string;
}

const PENDING_STATUS: InvitationStatus = { label: 'Pending', color: 'bg-amber-300' };
const INVITATION_STATUS: Record<string, InvitationStatus> = {
  true: { label: 'Accepted', color: 'bg-green-500' },
  false: { label: 'Rejected', color: 'bg-red-500' },
};

export function InvitationLists({ organizationId }: { organizationId: string }) {
  const [isInvitationsCollapsed, setIsInvitationsCollapsed] = useState<boolean>(false);

  const invitationList = useQuery({
    queryKey: [...currentUserQueryKey, 'invitations', organizationId],
    queryFn: () => getListInvitations(Number(organizationId)),
    enabled: true,
    retry: false,
  });

  if (invitationList.error instanceof ApiError) {
    return (
      <div className="max-w-full content-center p-5 text-center">
        <p>Organization haven't created invitation yet!</p>
      </div>
    );
  }

  return (
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
      <div className={`flex flex-row items-center justify-between gap-[15px] ${isInvitationsCollapsed ? 'hidden' : 'block'}`}>
        <table className="w-full table-fixed rounded-lg border border-[var(--sea-ink)] p-2 text-center">
          <thead>
            <tr>
              <th className="rounded-md border border-[var(--sea-ink)] p-2">Email</th>
              <th className="rounded-md border border-[var(--sea-ink)] p-2">Sent by (member id)</th>
              <th className="rounded-md border border-[var(--sea-ink)] p-2">Accepted</th>
            </tr>
          </thead>
          <tbody className="w-full">
            {invitationList.data?.map((invitation) => {
              const status = INVITATION_STATUS[String(invitation.accepted)] ?? PENDING_STATUS;
              return (
                <tr key={invitation.id} className="border border-[var(--sea-ink)]">
                  <td className="p-4">{invitation.email}</td>
                  <td className="p-4">{invitation.sender_name}</td>
                  <td className="p-4">
                    <span
                      className={`inline-block w-24 overflow-hidden text-ellipsis rounded-3xl border-2 p-2 ${status.color}`}
                    >
                      {status.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
