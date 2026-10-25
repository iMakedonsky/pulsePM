import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';
import { Topbar } from '#/components/topbar.tsx';
import { currentUserQueryKey, getCurrentUser } from '#/lib/auth-api.ts';

// `/_if_preceded_by_underscore_it_is_omitted_from_url/actual-url
// adding an underscore in front of route path segment serves purely logic purpose, it's excluded from the URL
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ context }) => {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      await context.queryClient.fetchQuery({
        queryKey: currentUserQueryKey,
        queryFn: getCurrentUser,
        retry: false,
      });
    } catch {
      throw redirect({ to: '/' });
    }
  },
  component: AuthenticatedLayout,
});

function AuthenticatedLayout() {
  return (
    <>
      <Topbar />
      <Outlet />
    </>
  );
}
