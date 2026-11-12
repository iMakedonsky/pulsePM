import { createFileRoute } from '@tanstack/react-router';
import { InvitationAcceptionBlock } from '#/components/UI/invitationAcceptionBlock.tsx';

export const Route = createFileRoute('/_public/invitation/$token')({
  component: InvitationRoute,
});

function InvitationRoute() {
  const { token } = Route.useParams();

  return <InvitationAcceptionBlock token={token} />;
}
