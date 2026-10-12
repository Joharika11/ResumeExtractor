
import pytest
from pydantic import ValidationError

from schemas import Resume


def test_valid_resume():
    resume = Resume.model_validate({
        "name": "Alex Kumar",
        "email": "alex@example.com",
        "skills": ["Python", "FastAPI"],
        "years_experience": 2,
    })

    assert resume.name == "Alex Kumar"
    assert str(resume.email) == "alex@example.com"
    assert resume.years_experience == 2


def test_missing_optional_fields_use_defaults():
    resume = Resume.model_validate({})

    assert resume.name is None
    assert resume.skills == []
    assert resume.education == []


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        Resume.model_validate({
            "email": "not-an-email",
        })


def test_negative_experience_is_rejected():
    with pytest.raises(ValidationError):
        Resume.model_validate({
            "years_experience": -1,
        })


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        Resume.model_validate({
            "unexpected_field": "value",
        })
