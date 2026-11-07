"""Every status code declared by the workspace API, with error messages checked against the OpenAPI docs."""

from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client

from api.openapi_docs import documented_messages, documented_statuses
from organizations.models import Member, Organization, WorkSpace
from users.models import User

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse

PASSWORD = 'Str0ng-pass-phrase!'
NOT_A_MEMBER = 'Current User is not a member of the Organization.'
NO_SUCH_WORKSPACE = 'Workspace with that ID does not exist.'
BLANK = 'This field cannot be blank.'

COLLECTION = '/api/organization/{org_id}/workspaces'
CREATE = '/api/organization/{org_id}/workspaces/create'
DETAIL = '/api/organization/{org_id}/workspaces/{workspace_id}'
UPDATE = '/api/organization/{org_id}/workspaces/{workspace_id}/update'
DELETE = '/api/organization/{org_id}/workspaces/{workspace_id}/delete'


# --- fixtures and helpers ----------------------------------------------------


@pytest.fixture
def owner() -> User:
    return User.objects.create_user(email='owner@example.com', password=PASSWORD)


@pytest.fixture
def organization(owner: User) -> Organization:
    return Organization.objects.create(owner=owner, name='Acme', description='Test org')


@pytest.fixture
def member(owner: User, organization: Organization) -> Member:
    return Member.objects.create(user=owner, organization=organization, role=Member.OrgRoles.OWNER)


@pytest.fixture
def workspace(member: Member) -> WorkSpace:
    return WorkSpace.objects.create(
        created_by=member,
        organization=member.organization,
        name='Engineering',
        space_code='ENG',
        icon_url='eng.png',
        description='Builders',
    )


@pytest.fixture
def outsider() -> User:
    """A user who belongs to a different organization, which has its own workspace."""
    user = User.objects.create_user(email='outsider@example.com', password=PASSWORD)
    other = Organization.objects.create(owner=user, name='Other', description='Other org')
    Member.objects.create(user=user, organization=other, role=Member.OrgRoles.OWNER)
    return user


@pytest.fixture
def foreign_workspace(outsider: User) -> WorkSpace:
    member = Member.objects.get(user=outsider)
    return WorkSpace.objects.create(
        created_by=member, organization=member.organization, name='Foreign', space_code='FRN', icon_url='frn.png'
    )


@pytest.fixture
def signed_in(client: Client, owner: User) -> Client:
    client.force_login(owner)
    return client


def url(org_id: object, workspace_id: object = None, action: str = '') -> str:
    base = f'/api/organization/{org_id}/workspaces'
    if workspace_id is None:
        return f'{base}/{action}' if action else base
    return f'{base}/{workspace_id}' + (f'/{action}' if action else '')


def payload(**overrides: Any) -> dict[str, Any]:
    return {'name': 'Design', 'space_code': 'DSN', 'icon_url': 'dsn.png', 'description': 'Designers', **overrides}


def assert_error(response: _MonkeyPatchedWSGIResponse, method: str, path: str, status: int, detail: str) -> None:
    """Check status and exact message, and that the message is one the OpenAPI docs list for this endpoint."""
    assert (response.status_code, response.json()) == (status, {'detail': detail})
    assert detail in documented_messages(method, path, status), f'{status} {detail!r} is not in the API docs'


def post(client: Client, path: str, body: dict[str, Any]) -> _MonkeyPatchedWSGIResponse:
    return client.post(path, body, content_type='application/json')


def patch(client: Client, path: str, body: dict[str, Any]) -> _MonkeyPatchedWSGIResponse:
    return client.patch(path, body, content_type='application/json')


# --- POST /{org_id}/workspaces/create ----------------------------------------


@pytest.mark.django_db
class TestCreateWorkspace:
    path = CREATE

    def test_declared_statuses(self) -> None:
        assert documented_statuses('post', self.path) == {200, 400, 403}

    @pytest.mark.usefixtures('member')
    def test_200_creates_workspace_owned_by_caller(self, signed_in: Client, organization: Organization) -> None:
        response = post(signed_in, url(organization.pk, action='create'), payload())

        assert response.status_code == 200
        body = response.json()
        assert (body['name'], body['space_code'], body['icon_url']) == ('Design', 'DSN', 'dsn.png')
        assert body['organization'] == organization.pk
        created = WorkSpace.objects.get(pk=body['id'])
        assert created.created_by.user.email == 'owner@example.com'

    @pytest.mark.usefixtures('member')
    @pytest.mark.parametrize(
        ('overrides', 'detail'),
        [
            ({'name': ''}, BLANK),
            ({'icon_url': ''}, BLANK),
            ({'description': ''}, BLANK),
            ({'space_code': 'TOOLNG'}, 'Ensure this value has at most 5 characters (it has 6).'),
        ],
    )
    def test_400_invalid_field(
        self, signed_in: Client, organization: Organization, overrides: dict[str, Any], detail: str
    ) -> None:
        response = post(signed_in, url(organization.pk, action='create'), payload(**overrides))
        assert_error(response, 'post', self.path, 400, detail)
        assert WorkSpace.objects.count() == 0

    @pytest.mark.usefixtures('member')
    def test_400_duplicate_space_code(
        self, signed_in: Client, organization: Organization, workspace: WorkSpace
    ) -> None:
        response = post(signed_in, url(organization.pk, action='create'), payload(space_code=workspace.space_code))
        assert_error(response, 'post', self.path, 400, 'Work space with this Space code already exists.')
        assert WorkSpace.objects.count() == 1

    def test_403_not_a_member(self, client: Client, outsider: User, organization: Organization) -> None:
        client.force_login(outsider)
        response = post(client, url(organization.pk, action='create'), payload())
        assert_error(response, 'post', self.path, 403, NOT_A_MEMBER)
        assert WorkSpace.objects.count() == 0

    @pytest.mark.usefixtures('member')
    def test_403_anonymous(self, client: Client, organization: Organization) -> None:
        response = post(client, url(organization.pk, action='create'), payload())
        assert_error(response, 'post', self.path, 403, NOT_A_MEMBER)


# --- GET /{org_id}/workspaces ------------------------------------------------


@pytest.mark.django_db
class TestListWorkspaces:
    path = COLLECTION

    def test_declared_statuses(self) -> None:
        assert documented_statuses('get', self.path) == {200, 400, 403, 404}

    def test_200_lists_only_this_organizations_workspaces(
        self, signed_in: Client, organization: Organization, workspace: WorkSpace, foreign_workspace: WorkSpace
    ) -> None:
        response = signed_in.get(url(organization.pk))

        assert response.status_code == 200
        assert [item['id'] for item in response.json()] == [workspace.pk]
        assert foreign_workspace.pk not in [item['id'] for item in response.json()]

    def test_400_non_numeric_org_id(self, signed_in: Client) -> None:
        assert_error(signed_in.get(url('abc')), 'get', self.path, 400, 'Invalid org_id.')

    def test_403_not_a_member(self, client: Client, outsider: User, organization: Organization) -> None:
        client.force_login(outsider)
        assert_error(client.get(url(organization.pk)), 'get', self.path, 403, NOT_A_MEMBER)

    @pytest.mark.usefixtures('member')
    def test_404_organization_without_workspaces(self, signed_in: Client, organization: Organization) -> None:
        response = signed_in.get(url(organization.pk))
        assert_error(response, 'get', self.path, 404, 'This organization has no workspaces yet.')

    @pytest.mark.usefixtures('member', 'foreign_workspace')
    def test_404_ignores_workspaces_of_other_organizations(self, signed_in: Client, organization: Organization) -> None:
        response = signed_in.get(url(organization.pk))
        assert_error(response, 'get', self.path, 404, 'This organization has no workspaces yet.')


# --- GET /{org_id}/workspaces/{workspace_id} ---------------------------------


@pytest.mark.django_db
class TestGetWorkspace:
    path = DETAIL

    def test_declared_statuses(self) -> None:
        assert documented_statuses('get', self.path) == {200, 400, 403, 404}

    def test_200_returns_workspace(self, signed_in: Client, organization: Organization, workspace: WorkSpace) -> None:
        response = signed_in.get(url(organization.pk, workspace.pk))

        assert response.status_code == 200
        assert response.json() == {
            'id': workspace.pk,
            'name': 'Engineering',
            'space_code': 'ENG',
            'created_by': workspace.created_by_id,
            'organization': organization.pk,
            'description': 'Builders',
            'icon_url': 'eng.png',
        }

    def test_400_non_numeric_org_id(self, signed_in: Client, workspace: WorkSpace) -> None:
        assert_error(signed_in.get(url('abc', workspace.pk)), 'get', self.path, 400, 'Invalid org_id.')

    def test_403_not_a_member(
        self, client: Client, outsider: User, organization: Organization, workspace: WorkSpace
    ) -> None:
        client.force_login(outsider)
        assert_error(client.get(url(organization.pk, workspace.pk)), 'get', self.path, 403, NOT_A_MEMBER)

    @pytest.mark.usefixtures('member')
    def test_404_unknown_workspace(self, signed_in: Client, organization: Organization) -> None:
        assert_error(signed_in.get(url(organization.pk, 99999)), 'get', self.path, 404, NO_SUCH_WORKSPACE)

    @pytest.mark.usefixtures('member')
    def test_404_workspace_of_another_organization(
        self, signed_in: Client, organization: Organization, foreign_workspace: WorkSpace
    ) -> None:
        response = signed_in.get(url(organization.pk, foreign_workspace.pk))
        assert_error(response, 'get', self.path, 404, NO_SUCH_WORKSPACE)


# --- PATCH /{org_id}/workspaces/{workspace_id}/update ------------------------


@pytest.mark.django_db
class TestUpdateWorkspace:
    path = UPDATE

    def test_declared_statuses(self) -> None:
        assert documented_statuses('patch', self.path) == {200, 400, 403, 404}

    def test_200_changes_only_the_given_fields(
        self, signed_in: Client, organization: Organization, workspace: WorkSpace
    ) -> None:
        response = patch(signed_in, url(organization.pk, workspace.pk, 'update'), {'name': 'Platform'})

        assert response.status_code == 200
        assert response.json()['name'] == 'Platform'
        workspace.refresh_from_db()
        assert (workspace.name, workspace.space_code, workspace.icon_url) == ('Platform', 'ENG', 'eng.png')

    def test_200_keeping_own_space_code_is_not_a_duplicate(
        self, signed_in: Client, organization: Organization, workspace: WorkSpace
    ) -> None:
        response = patch(signed_in, url(organization.pk, workspace.pk, 'update'), {'space_code': 'ENG'})
        assert response.status_code == 200

    @pytest.mark.parametrize(
        ('changes', 'detail'),
        [
            ({'name': ''}, BLANK),
            ({'space_code': 'TOOLNG'}, 'Ensure this value has at most 5 characters (it has 6).'),
        ],
    )
    def test_400_invalid_field_leaves_workspace_unchanged(
        self,
        signed_in: Client,
        organization: Organization,
        workspace: WorkSpace,
        changes: dict[str, Any],
        detail: str,
    ) -> None:
        response = patch(signed_in, url(organization.pk, workspace.pk, 'update'), changes)

        assert_error(response, 'patch', self.path, 400, detail)
        workspace.refresh_from_db()
        assert (workspace.name, workspace.space_code) == ('Engineering', 'ENG')

    def test_400_null_name(self, signed_in: Client, organization: Organization, workspace: WorkSpace) -> None:
        # Not listed in the docs examples; checked for the exact text only.
        response = patch(signed_in, url(organization.pk, workspace.pk, 'update'), {'name': None})

        assert (response.status_code, response.json()) == (400, {'detail': 'This field cannot be null.'})
        workspace.refresh_from_db()
        assert workspace.name == 'Engineering'

    def test_400_duplicate_space_code(
        self, signed_in: Client, organization: Organization, workspace: WorkSpace, member: Member
    ) -> None:
        WorkSpace.objects.create(
            created_by=member, organization=organization, name='Ops', space_code='OPS', icon_url='ops.png'
        )
        response = patch(signed_in, url(organization.pk, workspace.pk, 'update'), {'space_code': 'OPS'})

        assert_error(response, 'patch', self.path, 400, 'Work space with this Space code already exists.')
        workspace.refresh_from_db()
        assert workspace.space_code == 'ENG'

    def test_403_not_a_member_and_nothing_changes(
        self, client: Client, outsider: User, organization: Organization, workspace: WorkSpace
    ) -> None:
        client.force_login(outsider)
        response = patch(client, url(organization.pk, workspace.pk, 'update'), {'name': 'Hijacked'})

        assert_error(response, 'patch', self.path, 403, NOT_A_MEMBER)
        workspace.refresh_from_db()
        assert workspace.name == 'Engineering'

    @pytest.mark.usefixtures('member')
    def test_404_unknown_workspace(self, signed_in: Client, organization: Organization) -> None:
        response = patch(signed_in, url(organization.pk, 99999, 'update'), {'name': 'x'})
        assert_error(response, 'patch', self.path, 404, NO_SUCH_WORKSPACE)

    @pytest.mark.usefixtures('member')
    def test_404_workspace_of_another_organization_is_untouched(
        self, signed_in: Client, organization: Organization, foreign_workspace: WorkSpace
    ) -> None:
        response = patch(signed_in, url(organization.pk, foreign_workspace.pk, 'update'), {'name': 'Hijacked'})

        assert_error(response, 'patch', self.path, 404, NO_SUCH_WORKSPACE)
        foreign_workspace.refresh_from_db()
        assert foreign_workspace.name == 'Foreign'


# --- DELETE /{org_id}/workspaces/{workspace_id}/delete -----------------------


@pytest.mark.django_db
class TestDeleteWorkspace:
    path = DELETE

    def test_declared_statuses(self) -> None:
        assert documented_statuses('delete', self.path) == {200, 403, 404}

    def test_200_deletes_workspace(self, signed_in: Client, organization: Organization, workspace: WorkSpace) -> None:
        response = signed_in.delete(url(organization.pk, workspace.pk, 'delete'))

        assert response.status_code == 200
        assert response.content == b''
        assert not WorkSpace.objects.filter(pk=workspace.pk).exists()

    def test_403_not_a_member_and_workspace_survives(
        self, client: Client, outsider: User, organization: Organization, workspace: WorkSpace
    ) -> None:
        client.force_login(outsider)
        response = client.delete(url(organization.pk, workspace.pk, 'delete'))

        assert_error(response, 'delete', self.path, 403, NOT_A_MEMBER)
        assert WorkSpace.objects.filter(pk=workspace.pk).exists()

    @pytest.mark.usefixtures('member')
    def test_404_unknown_workspace(self, signed_in: Client, organization: Organization) -> None:
        response = signed_in.delete(url(organization.pk, 99999, 'delete'))
        assert_error(response, 'delete', self.path, 404, NO_SUCH_WORKSPACE)

    @pytest.mark.usefixtures('member')
    def test_404_workspace_of_another_organization_survives(
        self, signed_in: Client, organization: Organization, foreign_workspace: WorkSpace
    ) -> None:
        response = signed_in.delete(url(organization.pk, foreign_workspace.pk, 'delete'))

        assert_error(response, 'delete', self.path, 404, NO_SUCH_WORKSPACE)
        assert WorkSpace.objects.filter(pk=foreign_workspace.pk).exists()
