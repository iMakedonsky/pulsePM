import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import type { ReactNode } from 'react';
import { useToast } from '#/context/toast-context.ts';
import { acceptInvitation, getInvitation, type Invitation } from '#/lib/auth-api.ts';

export function InvitationBlock({ token }: { token: string }) {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const navigation = useNavigate();
  const queryKey = ['invitation', token] as const;

  const getInvitationData = useQuery({
    queryKey,
    queryFn: () => getInvitation(token),
  });

  const invitationData = getInvitationData.data;
  const acceptMutation = useMutation({
    mutationFn: (accepted: boolean) => acceptInvitation(token, accepted),
    onSuccess: async (invitationResponse) => {
      if (!invitationResponse.accepted) {
        await navigation({ to: '/' });
        return;
      }
      queryClient.setQueryData<Invitation>(queryKey, (invitation) =>
        invitation ? { ...invitation, accepted: invitationResponse.accepted } : invitation,
      );
      addToast(`Invitation was accepted!`, 'Success');
    },
    onError: (error) => addToast(error.message, 'Error'),
  });

  const renderShell = (children: ReactNode) => (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 lg:px-8">
      <div className="island-shell w-full max-w-md rounded-3xl border border-[var(--sea-ink)] p-8 text-center">
        <h1 className="display-title font-bold text-[32px]">Invitation</h1>
        <hr className="mt-4 border-[var(--line)] border-t" />
        <hr className="mt-1 border-[var(--line)] border-t" />
        {children}
      </div>
    </div>
  );

  // Validation order: request state first, then the data itself.
  // handle the error status with an access/not-found state instead of silently returning.
  if (getInvitationData.isPending || getInvitationData.isLoading) {
    return renderShell(<p>Loading invitation…</p>);
  }
  // accepted: null = pending, true = accepted, false = rejected
  if (invitationData?.accepted === false) {
    addToast(`Invitation is rejected!`, 'Error');
    return;
  }
  if (invitationData && new Date(invitationData.expired_at).getTime() < Date.now()) {
    addToast(`Invitation is rejected!`, 'Error');
    return;
  }

  return renderShell(
    <>
      <div className="form-group py-6">
        <h2 className="display-title font-semibold text-lg">{invitationData?.org_invite}</h2>
        <p className="mt-2 text-[var(--sea-ink-soft)]">{invitationData?.text_message}</p>
      </div>
      <div className="flex items-baseline justify-center gap-4">
        <button
          className="h-[200px] w-[200px] cursor-pointer rounded-[100px] border border-[var(--sea-ink)] px-6 py-2 hover:bg-[var(--sand)]"
          type="button"
          onClick={() => acceptMutation.mutate(true)}
        >
          Accept
        </button>
        <button
          className="h-[100px] w-[100px] cursor-pointer rounded-[50px] border border-[var(--sea-ink)] px-6 py-2 text-sm hover:bg-[var(--sand)]"
          type="button"
          onClick={() => acceptMutation.mutate(false)}
        >
          Reject
        </button>
      </div>
    </>,
  );
}
