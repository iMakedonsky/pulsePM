import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useToast } from '#/context/toast-context.ts';
import { getInvitation, type Invitation, respondToInvitation, tokenQueryKey } from '#/lib/auth-api';

interface InviteBlockProps {
  token: string;
}

export default function InviteBlock({ token }: InviteBlockProps) {
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const getInvitationData = useQuery({
    queryKey: [...tokenQueryKey, 'invitation', token],
    queryFn: () => getInvitation(token),
  });

  const invitationData = getInvitationData.data;
  const respondToInvitationMutation = useMutation({
    mutationFn: (accepted: boolean) => respondToInvitation(token, accepted),
    onSuccess: (response) => {
      queryClient.setQueryData<Invitation>([...tokenQueryKey, 'invitation', token], (invitation) =>
        invitation ? { ...invitation, accepted: response.accepted } : invitation,
      );
      addToast(response.accepted ? 'Invitation accepted!' : 'Invitation declined.', 'Success');
    },
    onError: (error) => addToast(error.message, 'Error'),
  });

  if (getInvitationData.isPending) {
    return renderInvitationPage('Loading invitation…');
  }

  if (getInvitationData.isError) {
    return renderInvitationPage(getInvitationData.error.message);
  }

  if (invitationData?.accepted !== null && invitationData?.accepted !== undefined) {
    return renderInvitationPage(
      <>
        <h1 className="display-title font-bold text-[32px]">Invitation</h1>
        <p className="mt-6 text-[var(--sea-ink-soft)]">
          This invitation has already been {invitationData.accepted ? 'accepted' : 'declined'}.
        </p>
      </>,
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 lg:px-8">
      <form
        className="island-shell w-full max-w-md rounded-3xl border border-[var(--sea-ink)] p-8 text-center"
        onSubmit={(e) => e.preventDefault()}
      >
        <h1 className="display-title font-bold text-[32px]">Invitation</h1>
        <hr className="mt-4 border-[var(--line)] border-t" />
        <hr className="mt-1 border-[var(--line)] border-t" />
        <div className="form-group py-6">
          <h2 className="display-title font-semibold text-lg">{invitationData?.org_invite}</h2>
          <p className="mt-2 text-[var(--sea-ink-soft)]">{invitationData?.text_message}</p>
        </div>
        <div className="flex justify-between gap-4">
          <button
            className="rounded-md border border-[var(--sea-ink)] px-6 py-2 hover:bg-[var(--sand)]"
            type="button"
            onClick={() => respondToInvitationMutation.mutate(true)}
            disabled={respondToInvitationMutation.isPending}
          >
            {respondToInvitationMutation.isPending ? 'Responding…' : 'Accept'}
          </button>
          <button
            className="rounded-md border border-[var(--sea-ink)] px-6 py-2 hover:bg-[var(--sand)]"
            type="button"
            onClick={() => respondToInvitationMutation.mutate(false)}
            disabled={respondToInvitationMutation.isPending}
          >
            Reject
          </button>
        </div>
      </form>
    </div>
  );
}

function renderInvitationPage(children: React.ReactNode) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 lg:px-8">
      <main className="island-shell w-full max-w-md rounded-3xl border border-[var(--sea-ink)] p-8 text-center">
        {children}
      </main>
    </div>
  );
}
