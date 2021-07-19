import pytest
from unittest.mock import Mock
from graphene_field_permission.api import check_field_access
from graphene_field_permission.decorators import has_field_access
from graphene_field_permission.fixtures import (
    graphene_field_permissions_allowed,
    graphene_field_permissions_failed,
)
from .fixtures import (
    info_mock,
    info_context_mock,
    orm_data_mock,
    single_info,
    single_permissions,
    fetch_permissions_single_permissions,
    orm_data_mock, user_permission_group_mock, user_permission_single_mock,
)


class TestFixtures:
    def setup(self):
        pass

    def test_has_field_access_decorator_allowed(
            self,
            info_mock,
            orm_data_mock,
            fetch_permissions_single_permissions,
            graphene_field_permissions_allowed
    ):
        # permission check exception for "permissionDoesNotExistInMock" in
        # "fetch_permissions_single_permissions" fixture is overridden
        # by graphene_field_permissions_allowed fixture
        @has_field_access('permissionDoesNotExistInMock')
        def test_method(data, info):
            pass

        test_method(orm_data_mock, info_mock)

    def test_has_field_access_decorator_failed(
            self,
            info_mock,
            orm_data_mock,
            fetch_permissions_single_permissions,
            graphene_field_permissions_failed
    ):
        # permission check success for permission1 "fetch_permissions_single_permissions"
        # is overridden by graphene_field_permissions_failed fixture
        @has_field_access('permission1')
        def test_method(data, info):
            pass

        with pytest.raises(Exception):
            test_method(orm_data_mock, info_mock)

    def test_check_field_access_failed(
            self,
            info_context_mock,
            single_permissions,
            graphene_field_permissions_failed
    ):
        # this should work normally as "permission1" is in the mocked
        # "single_permissions" but "graphene_field_permissions_allowed" fixture
        # allows it to succeed anyway
        with pytest.raises(PermissionError):
            check_field_access(
                'permission11',
                info_context=info_context_mock
            )

    def test_confirm_check_field_access_allowed(
            self,
            info_context_mock,
            single_permissions,
            graphene_field_permissions_allowed
    ):
        # this should not work normally as "permission11" is not in the mocked
        # "single_permissions", but "graphene_field_permissions_allowed" fixture
        # allows it to succeed anyway
        assert check_field_access(
            'permission11',
            info_context=info_context_mock
        ) is True
