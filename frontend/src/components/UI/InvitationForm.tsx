import { useMutation, useQueryClient } from '@tanstack/react-query';
import { type JSX, useId, useState } from 'react';
import { useToast } from '#/context/toast-context.ts';
import { createInvitation, currentUserQueryKey } from '@/lib/auth-api';

export function InvitationForm({
  organizationId,
  isInvitationFormVisible,
  onClose,
}: {
  organizationId: number;
  isInvitationFormVisible: boolean;
  onClose: () => void;
}): JSX.Element {
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const [inviteeEmail, setInviteeEmail] = useState<string>('');
  const [textMessage, setTextMessage] = useState<string>('');

  const uid = useId();
  const formId = `${uid}-form`;
  const emailId = `${uid}-email`;
  const messageId = `${uid}-message`;

  const createInvitationMutation = useMutation({
    mutationFn: () => createInvitation(organizationId, inviteeEmail, textMessage),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [...currentUserQueryKey, 'invitations', String(organizationId)],
      });
      setInviteeEmail('');
      setTextMessage('');

      addToast(`Invitation was sent successfully!`, 'Success');
      onClose();
    },
    onError: (error) => {
      addToast(error.message, 'Error');
    },
  });

  return (
    <div
      className={`fixed inset-0 z-40 items-center justify-center bg-black/30 backdrop-blur-sm ${isInvitationFormVisible ? 'flex' : 'hidden'}`}
    >
      <div className="relative rounded-xl border border-[var(--line)] bg-[var(--foam)]">
        <button
          aria-label="Close invitation form"
          className="absolute top-2 right-2 cursor-pointer"
          onClick={onClose}
          type="button"
        >
          X
        </button>
        <form
          id={formId}
          name="invitation"
          className="flex flex-col items-center gap-4 p-20"
          onSubmit={(event) => {
            event.preventDefault();
            createInvitationMutation.mutate();
          }}
        >
          <h2 className="text-3xl">Invite member</h2>
          <div className="flex flex-col">
            <label htmlFor={emailId}>Email</label>
            <input
              id={emailId}
              className="rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              type="email"
              value={inviteeEmail}
              onChange={(event) => setInviteeEmail(event.target.value)}
              placeholder="Email"
              required
            />
          </div>
          <div className="flex w-full flex-col">
            <label htmlFor={messageId}>Message</label>
            <textarea
              id={messageId}
              className="w-full rounded-md border border-[var(--line)] bg-white px-2 py-1.5 text-sm"
              value={textMessage}
              onChange={(event) => setTextMessage(event.target.value)}
              placeholder="Invitation :)"
              maxLength={500}
            />
          </div>
          <button
            aria-label="Send invitation"
            type="submit"
            className="mt-[25px] cursor-pointer rounded-md bg-[var(--lagoon-deep)] px-3 py-2 font-semibold text-sm text-white"
            disabled={createInvitationMutation.isPending}
          >
            {createInvitationMutation.isPending ? '...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}
