import { createFileRoute, Outlet } from '@tanstack/react-router';
import { Topbar } from '#/components/topbar.tsx';
// `/_if_preceded_by_underscore_it_is_omitted_from_url/actual-url
// adding an underscore in front of route path segment serves purely logic purpose, it's excluded from the URL
export const Route = createFileRoute('/_public')({
  component: PublicLayout,
});

function PublicLayout() {
  return (
    <>
      <Topbar />
      <Outlet />
    </>
  );
}
