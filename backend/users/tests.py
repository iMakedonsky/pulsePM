import pytest
from django.contrib.auth import authenticate, get_user_model


@pytest.mark.django_db
def test_user_uses_email_as_login_identifier() -> None:
    user = get_user_model().objects.create_user(email='person@example.com', password='safe-password')

    assert user.username is None
    assert user.email == 'person@example.com'
    assert authenticate(username='person@example.com', password='safe-password') == user


@pytest.mark.django_db
def test_email_is_required() -> None:
    with pytest.raises(ValueError, match='email address'):
        get_user_model().objects.create_user(email='', password='safe-password')
