import pytest
import sys
from unittest.mock import Mock

from mocks import django_empty_conf_mock, django_missing_src_module_conf_mock,\
    django_missing_src_method_conf_mock, django_valid_conf_mock,\
    user_permission_single_mock, logger_mock
from graphene_field_permission.permissions_loader import\
    import_django_settings, import_settings, get_permissions_method


@pytest.fixture
def logger():
    return logger_mock()


@pytest.fixture
def user():
    return Mock()


class TestPermissionsLoader:
    def test_import_django_settings(self):
        # missing django.conf should throw an exception
        if 'django.conf' in sys.modules:
            del sys.modules['django.conf']
        with pytest.raises(ImportError):
            import_django_settings()

        # missing settings.GRAPHENE_FIELD_PERMISSION should throw exception
        sys.modules['django.conf'] = django_empty_conf_mock()
        with pytest.raises(AttributeError):
            import_django_settings()

        # missing GRAPHENE_FIELD_PERMISSION.SRC_MODULE
        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_missing_src_module_conf_mock()
        with pytest.raises(KeyError):
            import_django_settings()

        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_missing_src_method_conf_mock()
        with pytest.raises(KeyError):
            import_django_settings()

        # valid django details
        sys.modules['django.conf'] = django_valid_conf_mock()
        results = import_django_settings()
        src_mod, src_method = results
        assert src_mod == 'fakemod'
        assert src_method is 'fakemethod'

    def test_import_settings(self):
        # Check that no settings found throws ImportError exception
        if 'django.conf' in sys.modules:
            del sys.modules['django.conf']
        with pytest.raises(ImportError):
            import_settings()

        # django framework
        sys.modules['django.conf'] = django_valid_conf_mock()
        src_mod, src_method = import_settings()
        assert src_mod == 'fakemod'
        assert src_method == 'fakemethod'

        # add tests for additional frameworks here #


def test_get_permissions_method():
    # missing django.conf should throw an exception
    if 'django.conf' in sys.modules:
        del sys.modules['django.conf']
    with pytest.raises(Exception):
        get_permissions_method()

    # missing settings.GRAPHENE_FIELD_PERMISSION should throw exception
    sys.modules['django.conf'] = django_empty_conf_mock()
    with pytest.raises(Exception):
        get_permissions_method()

    # missing GRAPHENE_FIELD_PERMISSION.SRC_MODULE
    del sys.modules['django.conf']
    sys.modules['django.conf'] = django_missing_src_module_conf_mock()
    with pytest.raises(Exception):
        get_permissions_method()

    # test missing GRAPHENE_FIELD_PERMISSION.SRC_METHOD
    del sys.modules['django.conf']
    sys.modules['django.conf'] = django_missing_src_method_conf_mock()
    with pytest.raises(Exception):
        get_permissions_method()

    # valid django details but missing module+method
    del sys.modules['django.conf']
    if 'fakemod' in sys.modules:
        del sys.modules['fakemod']
    sys.modules['django.conf'] = django_valid_conf_mock()
    with pytest.raises(Exception):
        user_permissions_func = get_permissions_method()
        user_permissions_func()

    # the same valid django details but with module+method
    fakemod = Mock(spec=[])
    fakemod.fakemethod = user_permission_single_mock
    sys.modules['fakemod'] = fakemod
    user_permissions_func = get_permissions_method()
    permission_list = user_permissions_func()

    assert 'permission1' in permission_list
    assert 'permission2' in permission_list
    assert 'permission3' in permission_list
