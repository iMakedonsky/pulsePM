from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import validate_not_past


def test_due_date_validator_accepts_today() -> None:
    validate_not_past(timezone.localdate())


def test_due_date_validator_rejects_past_dates() -> None:
    with pytest.raises(ValidationError, match='cannot be in the past'):
        validate_not_past(timezone.localdate() - timedelta(days=1))
