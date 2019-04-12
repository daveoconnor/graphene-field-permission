import importlib
import pytest
import sys
from unittest import mock
from unittest.mock import Mock

import mocks
from graphene_field_permission.tests.mocks import user_permission_group_mock,\
    user_permission_single_mock


@pytest.fixture
def logger():
    return mocks.logger_mock()


@pytest.fixture
def user():
    return Mock()


@pytest.fixture
def django_mock():
    return mocks.django_empty_conf_mock()


@pytest.fixture
def django_valid_conf_mock():
    return mocks.django_valid_conf_mock()


class TestPermissionsMiddleware():
    def test_on_error(self, logger, django_mock):
        sys.modules['django.conf'] = django_mock
        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        with mock.patch.object(logger, 'error') as mock_error:
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.on_error('this is an error')
            mock_error.assert_called_once_with('this is an error')

    def test_resolve(self, django_valid_conf_mock):
        next = Mock()
        root = Mock()
        info = Mock()
        info.context.user.id = 1
        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_valid_conf_mock

        # test ungrouped user
        fakemod = Mock(spec=[])
        fakemod.fakemethod = user_permission_single_mock
        sys.modules['fakemod'] = fakemod

        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        pm.resolve(next, root, info)

        assert 'permission1' in pm.permissions
        assert 'permission2' in pm.permissions
        assert 'permission3' in pm.permissions
        # run twice and check permissions remain set
        pm.resolve(next, root, info)
        assert 'permission1' in pm.permissions
        assert 'permission2' in pm.permissions
        assert 'permission3' in pm.permissions

        # test grouped user
        fakemod = Mock(spec=[])
        fakemod.fakemethod = user_permission_group_mock
        sys.modules['fakemod'] = fakemod

        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        pm.resolve(next, root, info)

        assert 'permission1' in pm.permissions['group-1234']
        assert 'permission2' in pm.permissions['group-1234']
        assert 'permission4' not in pm.permissions['group-1234']
        # run twice and check permissions remain set
        pm.resolve(next, root, info)
        assert 'permission4' in pm.permissions['group-5678']
        assert 'permission5' in pm.permissions['group-5678']
        assert 'permission3' not in pm.permissions['group-5678']
