import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/organization')({
  component: OrganizationDashboard,
})

// TODO: Add organization data fetch request in auth_api
function OrganizationDashboard() {
  const { id } = Route.useParams()
  return <div>Hello "/organization"!</div>
}
