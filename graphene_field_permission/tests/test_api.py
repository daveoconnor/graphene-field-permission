import pytest
import graphene_field_permission.permissions_loader
from unittest.mock import Mock
from graphene_field_permission.api import (
    _has_access, permissions_filter,
    get_filter_data, check_field_access,
    restructure_permissions,
    fetch_permissions,
)
from graphene_field_permission.tests.fixtures import (
    group_permissions,
    single_permissions,
    info_context_mock,
    user_permission_group_mock,
    user_permission_single_mock,
    structured_group_permission_data,
    structured_single_permission_data,
)


class TestApi:
    def test_permissions_filter(
            self,
            user_permission_group_mock,
    ):
        permissions = permissions_filter(
            user_permission_group_mock,
            'group-1234'
        )
        assert 'permission1' in permissions
        assert 'permission2' in permissions
        assert 'permission3' in permissions
        assert 'permission4' not in permissions
        assert 'permission5' not in permissions
        assert 'permission6' not in permissions

        permissions2 = permissions_filter(
            user_permission_group_mock,
            'group-5678'
        )
        assert 'permission1' not in permissions2
        assert 'permission2' not in permissions2
        assert 'permission3' not in permissions2
        assert 'permission4' in permissions2
        assert 'permission5' in permissions2
        assert 'permission6' in permissions2

        # test that an exception is raised on incorrect key access
        with pytest.raises(Exception):
            permissions_filter(
                user_permission_group_mock,
                'group-NONE'
            )

    def test_get_filter_data(self):
        # test a single level
        test_data = Mock()
        test_data.id = 'foo'
        assert get_filter_data(
            test_data,
            'id'
        ) == 'foo'

        # test multiple levels
        test_data = Mock()
        test_data.group.division.corporation.id = 'foo'
        assert get_filter_data(
            test_data,
            'group.division.corporation.id'
        ) == 'foo'
        # test missing relation works
        with pytest.raises(Exception):
            # test multiple levels
            get_filter_data(
                {},
                'two.steps.beyond'
            )

    def test__has_access(self, user_permission_group_mock):
        assert _has_access(
            'permission1',
            user_permissions={'permission1': True},
        ) is True
        assert _has_access(
            'permission1',
            user_permissions=structured_group_permission_data,
            filter_id='group-1234'
        ) is True
        # test to ensure OR functionality
        assert _has_access(
            'permission1',
            'permission5',
            user_permissions=structured_group_permission_data,
            filter_id='group-5678'
        ) is True

        with pytest.raises(PermissionError):
            _has_access(
                'permission2',
                user_permissions={'permission1': True},
            )

    def test_restructure_permissions(
            self,
            user_permission_single_mock,
            user_permission_group_mock
    ):
        results = restructure_permissions(user_permission_single_mock)
        assert results['permission1'] is True
        assert results['permission2'] is True
        assert results['permission3'] is True

        results = restructure_permissions(user_permission_group_mock)
        assert results['group-1234']['permission1'] is True
        assert results['group-1234']['permission3'] is True
        assert results['group-5678']['permission5'] is True
        assert results['group-5678']['permission6'] is True

    def test_fetch_permissions(self, monkeypatch):
        def mock_permissions_method():
            return Mock(return_value=['foo', 'bar', 'fam'])
        with monkeypatch.context() as m:
            m.setattr(
                graphene_field_permission.permissions_loader,
                'get_permissions_method',
                mock_permissions_method
            )
            user = Mock()
            permissions = fetch_permissions(user)

            assert 'foo' in permissions.keys()
            assert 'bar' in permissions.keys()
            assert 'fam' in permissions.keys()

        def mock_permissions_method():
            return Mock(return_value={
                'test1': ['foo', 'bar', 'fam'],
                'test2': ['x', 'y', 'z'],
            })
        with monkeypatch.context() as m:
            m.setattr(
                graphene_field_permission.permissions_loader,
                'get_permissions_method',
                mock_permissions_method
            )
            user = Mock()
            permissions = fetch_permissions(user)
            assert 'foo' in permissions['test1'].keys()
            assert 'bar' in permissions['test1'].keys()
            assert 'fam' in permissions['test1'].keys()
            assert 'x' in permissions['test2'].keys()
            assert 'y' in permissions['test2'].keys()
            assert 'z' in permissions['test2'].keys()
            assert 'foo' not in permissions['test2'].keys()
            assert 'x' not in permissions['test1'].keys()


    def test_check_field_access_single(
            self,
            single_permissions,
            info_context_mock
    ):
        # single level of permissions
        assert check_field_access(
            'permission1',
            info_context=info_context_mock
        ) is True

        # no matching permission
        with pytest.raises(PermissionError):
            check_field_access(
                'fail',
                info_context=info_context_mock
            )

    def test_check_field_access_group(
            self,
            group_permissions,
            info_context_mock
    ):
        test_data = Mock()
        test_data.group.division.corporation.id = 'group-5678'

        assert check_field_access(
            'permissionN',
            'permission4',
            filter_field='group.division.corporation.id',
            filter_data=test_data,
            info_context=info_context_mock,
        ) is True

        # ensure filter_data check works
        with pytest.raises(AttributeError):
            check_field_access(
                'permissionXX',
                'permission4',
                filter_field='group.division.corporation.id',
                info_context=info_context_mock,
            )
