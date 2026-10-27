import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';
import { currentUserQueryKey, getCurrentUser } from '#/lib/auth-api.ts';

export const Route = createFileRoute('/_authentificated')({
  beforeLoad: async ({ context }) => {
    try {
      await context.queryClient.query({
        queryKey: currentUserQueryKey,
        queryFn: getCurrentUser,
        retry: false,
      });
    } catch {
      throw redirect({
        to: '/',
      });
    }
  },
  component: AuthenticateRoute,
});

function AuthenticateRoute() {
  return <Outlet />;
}
