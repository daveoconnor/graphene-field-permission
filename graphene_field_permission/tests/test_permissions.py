import importlib
import pytest
import sys
from unittest import mock
from unittest.mock import Mock

from .fixtures import (
    django_empty_conf,
    django_valid_conf,
    logger,
    single_permission_data,
    group_permission_data,
)


class TestPermissionsMiddleware:
    def test_on_error(self, logger):
        sys.modules['django.conf'] = django_empty_conf
        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        with mock.patch.object(logger, 'error') as mock_error:
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.on_error('this is an error')
            mock_error.assert_called_once_with('this is an error')

    def test_resolve(self, django_valid_conf):
        next = Mock()
        root = Mock()
        info = Mock()
        info.context.user.id = 1
        # del sys.modules['django.conf']
        sys.modules['django.conf'] = django_valid_conf

        # test ungrouped user
        fakemod = Mock(spec=[])
        fakemod.fakemethod = Mock(return_value=single_permission_data)
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
        fakemod.fakemethod = Mock(return_value=group_permission_data)
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
