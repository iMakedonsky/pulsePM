from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import Http404, HttpError

from organizations.models import Member, Organization
from organizations.schema import OrganizationSchema

router = Router(tags=['Organizations'])


@router.get('/organization/{org_id}', response={200: OrganizationSchema, 404: dict})
def get_organization(request: HttpRequest, org_id: int):
    membership_check = Member.objects.filter(user=request.user.pk, organization=org_id)
    if not membership_check.exists():
        raise HttpError(404, 'Current User is not a member of the Organization.')
    try:
        organization = get_object_or_404(Organization, pk=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Organization with that ID does not exist.') from exc
    return OrganizationSchema.from_organization_instance(organization)


@router.get('workspacea', response={200: dict})
def workspace_view(request, *args, **kwargs):
    workspace = request.GET.get('workspace')