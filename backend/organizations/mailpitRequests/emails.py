from http import HTTPStatus
from typing import Any

import requests
from django.core import signing
from requests import HTTPError, RequestException

from conf.settings import EMAIL_HTTP_PORT, EMAIL_SERVICE_HOST, FROM_EMAIL, FRONTED_ORIGIN
from organizations.models import OrgInvitation

BAD_GATEWAY = HTTPStatus.BAD_GATEWAY.value


class InvitationEmailError(Exception):
    def __init__(self, status_code: int, text: str | None = None, exception_object: Exception | None = None) -> None:
        super().__init__(text)

        self.status_code = status_code
        self.text = text
        self.exception_object = exception_object


def send_invitation_email(invitation_data: OrgInvitation) -> None:
    encode_id = signing.dumps(invitation_data.id.int)
    payload: dict[str, Any] = {
        'from': {
            'Email': FROM_EMAIL,
            'Name': FROM_EMAIL,
        },
        'to': [
            {
                'Email': invitation_data.email.lower(),
                'Name': invitation_data.email.lower(),
            }
        ],
        'subject': f'Invitation to org {invitation_data.org_invite}',
        'text': str(invitation_data.text_message + '\n' + f'{FRONTED_ORIGIN}/invitation/{encode_id}'),
    }
    try:
        response = requests.post(f'http://{EMAIL_SERVICE_HOST}:{EMAIL_HTTP_PORT}/api/v1/send', json=payload, timeout=5)
        response.raise_for_status()
    except HTTPError as exc:
        if exc.response is None:
            raise InvitationEmailError(status_code=BAD_GATEWAY, text=str(exc), exception_object=exc) from exc
        raise InvitationEmailError(status_code=exc.response.status_code, text=exc.response.text) from exc
    except RequestException as exc:
        # Connection errors and timeouts never receive a response, so there is no upstream status to forward.
        raise InvitationEmailError(status_code=BAD_GATEWAY, text=str(exc), exception_object=exc) from exc
