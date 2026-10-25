import { createFileRoute } from '@tanstack/react-router';
import InviteBlock from '#/components/invite.tsx';

export const Route = createFileRoute('/_authenticated/invitation/$token')({
  component: RouteComponent,
});

function RouteComponent() {
  const { token } = Route.useParams();
  return <InviteBlock token={token} />;
}
