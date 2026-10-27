import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import type { ReactNode } from 'react';
import { useToast } from '#/context/toast-context.ts';
import { acceptInvitation, getInvitation, type Invitation } from '#/lib/auth-api.ts';

export function InvitationBlock({ token }: { token: string }) {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const navigation = useNavigate({ from: '/invitation/$token' });
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
      await navigation({ to: `/organization/${invitationData?.org_invite}` });
    },
    onError: async (error) => {
      addToast(error.message, 'Error');
      await navigation({ to: '/' });
    },
  });

  const renderShell = (children: ReactNode) => (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 lg:px-8">
      <div className="island-shell w-full max-w-md rounded-3xl border border-[var(--sea-ink)] p-8 text-center">
        <h1 className="display-title font-bold text-[32px]">Invitation</h1>
        <hr className="mt-2 mb-5 border-[var(--line)] border-t" />
        {children}
      </div>
    </div>
  );

  const errorMessageComp = (errorMessage: string) => (
    <div>
      <h3 className="display-title font-semibold text-lg">Error</h3>
      <p className="mt-2 text-[var(--sea-ink-soft)]">{errorMessage}</p>
    </div>
  );

  if (getInvitationData.isPending || getInvitationData.isLoading) {
    return renderShell(<p>Loading invitation…</p>);
  }

  if (getInvitationData.isError) {
    return renderShell(errorMessageComp(getInvitationData.error.message));
  }

  return renderShell(
    <>
      <div className="form-group py-6">
        <h2 className="display-title font-semibold text-lg">Invited to org name: {invitationData?.org_name}</h2>
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
