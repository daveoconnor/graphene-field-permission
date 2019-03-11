import importlib
import logging
import pytest
import sys
from unittest import mock
from unittest.mock import Mock


@pytest.fixture
def logger():
    return logging.getLogger('graphene_field_permission.permissions')


class TestPermissionsMiddleware():
    def test_on_error(self, monkeypatch, logger):
        django_mock = Mock()
        sys.modules['django.conf'] = django_mock
        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        with mock.patch.object(logger, 'error') as mock_error:
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.on_error('this is an error')
            mock_error.assert_called_once_with('this is an error')

    def test___fetch_permissions(self, monkeypatch, logger):
        # instances of things that can be re-used
        user = Mock()
        fakemod = Mock()

        # TODO: add test for missing GRAPHENE_FIELD_PERMISSION setting
        # test missing GRAPHENE_FIELD_PERMISSION values
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings = Mock(side_effect=KeyError)
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {}
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm._PermissionsMiddleware__fetch_permissions(
                user
            )

        # test missing GRAPHENE_FIELD_PERMISSION src method values
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings = Mock(side_effect=KeyError)
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'fakemod',
            }
            sys.modules['django.conf'] = django_mock
            sys.modules['fakemod'] = fakemod
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm._PermissionsMiddleware__fetch_permissions(
                user
            )

        # test missing user permissions module
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'non_module',
                'SRC_METHOD': 'get_user_permissions'
            }
            sys.modules['fakemod'] = fakemod
            sys.modules['django.conf'] = django_mock
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.settings = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm._PermissionsMiddleware__fetch_permissions(
                user
            )

        # test missing user permissions function
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'sys',
                'SRC_METHOD': 'non_method'
            }
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.settings = django_mock
            with mock.patch.object(logger, 'error') as mock_error:
                pm._PermissionsMiddleware__fetch_permissions(
                    user
                )
                msg = 'SRC_METHOD non_method not found on sys'
                mock_error.assert_called_once_with(msg)

        # set up working module
        fakemod.get_user_permissions = lambda _: [
            'permission1',
            'permission2',
            'permission3'
        ]
        django_mock = Mock()
        django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
            'SRC_MODULE': 'fakemod',
            'SRC_METHOD': 'get_user_permissions'
        }
        sys.modules['django.conf'] = django_mock

        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        pm.settings = django_mock
        import graphene_field_permission.permissions   # noqa
        importlib.reload(graphene_field_permission.permissions)
        pm._PermissionsMiddleware__fetch_permissions(
            user
        )
        assert 'permission1' in pm.permissions
        assert 'permission2' in pm.permissions
        assert 'permission3' in pm.permissions

    def test_resolve(self):
        fakemod_resolve = Mock()
        fakemod_resolve.get_user_permissions_resolve = lambda _: [
            'permission11',
            'permission12',
            'permission13'
        ]
        django_mock = Mock()
        django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
            'SRC_MODULE': 'fakemod_resolve',
            'SRC_METHOD': 'get_user_permissions_resolve'
        }
        sys.modules['django.conf'] = django_mock
        sys.modules['fakemod_resolve'] = fakemod_resolve

        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        next = Mock()
        root = Mock()
        info = Mock()
        info.context.user.id = 1
        pm.resolve(next, root, info)

        assert 'permission11' in pm.permissions
        assert 'permission12' in pm.permissions
        assert 'permission13' in pm.permissions
        # run twice and check permissions remain set
        pm.resolve(next, root, info)
        assert 'permission11' in pm.permissions
        assert 'permission12' in pm.permissions
        assert 'permission13' in pm.permissions
