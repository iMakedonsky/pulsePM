import { createFileRoute } from '@tanstack/react-router';
import { InvitationBlock } from '#/components/UI/invitationBlock.tsx';

export const Route = createFileRoute('/_public/invitation/$token')({
  component: InvitationRoute,
});

function InvitationRoute() {
  const { token } = Route.useParams();

  return <InvitationBlock token={token} />;
}
