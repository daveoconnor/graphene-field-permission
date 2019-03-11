import importlib
import logging
import pytest
import sys
from unittest import mock
from unittest.mock import Mock, PropertyMock


@pytest.fixture
def logger():
    return logging.getLogger('graphene_field_permission.permissions')


@pytest.fixture
def user():
    return Mock()


@pytest.fixture
def django_mock():
    django_mock = Mock()
    django_mock.settings = Mock(spec=[])
    return django_mock


class TestPermissionsMiddleware():
    def test_on_error(self, monkeypatch, logger, django_mock):
        sys.modules['django.conf'] = django_mock
        import graphene_field_permission.permissions
        importlib.reload(graphene_field_permission.permissions)
        with mock.patch.object(logger, 'error') as mock_error:
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.on_error('this is an error')
            mock_error.assert_called_once_with('this is an error')

    def test___import_django_settings(self, django_mock):
        # missing django.conf should throw an exception
        with pytest.raises(ImportError):
            del sys.modules['django.conf']
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm._PermissionsMiddleware__import_django_settings()

        # missing settings.GRAPHENE_FIELD_PERMISSION should throw exception
        with pytest.raises(AttributeError):
            django_mock.settings = Mock(spec=[])
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm._PermissionsMiddleware__import_django_settings()

        # missing GRAPHENE_FIELD_PERMISSION.SRC_MODULE
        with pytest.raises(KeyError):
            django_mock.settings = Mock(spec=[])
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {}
            del sys.modules['django.conf']
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            results = pm._PermissionsMiddleware__import_django_settings()
            src_mod, src_method = results

        # missing GRAPHENE_FIELD_PERMISSION.SRC_METHOD
        with pytest.raises(KeyError):
            django_mock.settings = Mock(spec=[])
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'fakemod'
            }
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            results = pm._PermissionsMiddleware__import_django_settings()
            src_mod, src_method = results

        # working django details
        django_mock.settings = Mock(spec=[])
        django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
            'SRC_MODULE': 'fakemod',
            'SRC_METHOD': 'fakemethod'
        }
        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_mock
        import graphene_field_permission.permissions   # noqa
        importlib.reload(graphene_field_permission.permissions)
        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        results = pm._PermissionsMiddleware__import_django_settings()
        src_mod, src_method = results
        assert src_mod == 'fakemod'
        assert src_method is 'fakemethod'

    def test___import_settings(self, django_mock):
        # test that no settings found throws ImportError exception
        with pytest.raises(ImportError):
            del sys.modules['django.conf']
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            src_mod, src_method = pm._PermissionsMiddleware__import_settings()

        # test django framework
        django_mock.settings = Mock(spec=[])
        django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
            'SRC_MODULE': 'fakemod',
            'SRC_METHOD': 'fakemethod'
        }
        sys.modules['django.conf'] = django_mock
        import graphene_field_permission.permissions   # noqa
        importlib.reload(graphene_field_permission.permissions)
        pm = graphene_field_permission.permissions.PermissionsMiddleware()
        src_mod, src_method = pm._PermissionsMiddleware__import_settings()
        assert src_mod == 'fakemod'
        assert src_method == 'fakemethod'

        # add tests for additional frameworks here

    def test___fetch_permissions(self, monkeypatch, django_mock, logger, user):
        # instances of things that can be re-used
        fakemod = Mock()

        # missing any valid configuration settings should throw an exception
        with pytest.raises(Exception):
            del sys.modules['django.conf']
            # add del for other settings modules here
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm._PermissionsMiddleware__fetch_permissions(user)

        # test django but with GRAPHENE_FIELD_PERMISSION missing
        with pytest.raises(Exception):
            django_mock.settings = Mock(spec=[])
            django_mock.settings
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            results = pm._PermissionsMiddleware__fetch_permissions(user)
            src_mod, src_method = results

        # test django but with permissions settings values missing
        with pytest.raises(Exception):
            django_mock.settings = Mock(spec=[])
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {}
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            results = pm._PermissionsMiddleware__fetch_permissions(user)
            src_mod, src_method = results

        # test missing user permissions module
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'nonexistant',
                'SRC_METHOD': 'noop'
            }
            del sys.modules['django.conf']
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

        # test missing user permissions function
        with pytest.raises(Exception):
            django_mock = Mock()
            django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
                'SRC_MODULE': 'sys',
                'SRC_METHOD': 'noop'
            }
            del sys.modules['django.conf']
            sys.modules['django.conf'] = django_mock
            import graphene_field_permission.permissions   # noqa
            importlib.reload(graphene_field_permission.permissions)
            pm = graphene_field_permission.permissions.PermissionsMiddleware()
            pm.settings = django_mock
            with mock.patch.object(logger, 'error') as mock_error:
                pm._PermissionsMiddleware__fetch_permissions(
                    user
                )
                msg = 'SRC_METHOD noop not found on sys'
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
        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_mock
        sys.modules['fakemod'] = fakemod

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
        del sys.modules['django.conf']
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
