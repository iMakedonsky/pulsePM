from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from .models import validate_not_past


def test_due_date_validator_accepts_today() -> None:
    validate_not_past(date.today())


def test_due_date_validator_rejects_past_dates() -> None:
    with pytest.raises(ValidationError, match='cannot be in the past'):
        validate_not_past(date.today() - timedelta(days=1))
