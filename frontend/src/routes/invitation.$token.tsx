import { useQuery } from '@tanstack/react-query';
import { createFileRoute } from '@tanstack/react-router';
import { getInvitation, tokenQueryKey } from '#/lib/auth-api.ts';

export const Route = createFileRoute('/invitation/$token')({
  component: RouteComponent,
});

function RouteComponent() {
  const { token } = Route.useParams();

  const getInvitationData = useQuery({
    queryKey: [...tokenQueryKey, 'invitation', token],
    queryFn: () => getInvitation(token),
  });

  const invitationData = getInvitationData.data;
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
          <button className="rounded-md border border-[var(--sea-ink)] px-6 py-2 hover:bg-[var(--sand)]" type="submit">
            Accept
          </button>
          <button className="rounded-md border border-[var(--sea-ink)] px-6 py-2 hover:bg-[var(--sand)]" type="submit">
            Reject
          </button>
        </div>
      </form>
    </div>
  );
}
