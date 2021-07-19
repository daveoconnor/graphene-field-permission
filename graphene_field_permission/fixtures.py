import pytest
from unittest.mock import MagicMock


@pytest.fixture
def graphene_field_permissions_allowed(monkeypatch):
    monkeypatch.setattr(
        "graphene_field_permission.api._has_access",
        MagicMock(return_value=True),
    )


@pytest.fixture
def graphene_field_permissions_failed(monkeypatch):
    monkeypatch.setattr(
        "graphene_field_permission.api._has_access",
        MagicMock(side_effect=PermissionError),
    )
