import pytest
import sys
from unittest.mock import Mock

from .fixtures import (
    django_empty_conf,
    django_missing_src_method_conf,
    django_missing_src_module_conf,
    django_valid_conf,
    user_permission_single_mock,
)
from graphene_field_permission.permissions_loader import (
    import_django_settings,
    import_settings,
    get_permissions_method
)


class TestPermissionsLoader:
    def test_import_django_settings(
            self,
            django_empty_conf,
            django_missing_src_module_conf,
            django_missing_src_method_conf,
            django_valid_conf
    ):
        # missing django.conf should throw an exception
        if 'django.conf' in sys.modules:
            del sys.modules['django.conf']
        with pytest.raises(ImportError):
            import_django_settings()

        # missing settings.GRAPHENE_FIELD_PERMISSION should throw exception
        sys.modules['django.conf'] = django_empty_conf
        with pytest.raises(AttributeError):
            import_django_settings()

        # missing GRAPHENE_FIELD_PERMISSION.SRC_MODULE
        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_missing_src_module_conf
        with pytest.raises(KeyError):
            import_django_settings()

        del sys.modules['django.conf']
        sys.modules['django.conf'] = django_missing_src_method_conf
        with pytest.raises(KeyError):
            import_django_settings()

        # valid django details
        sys.modules['django.conf'] = django_valid_conf
        results = import_django_settings()
        src_mod, src_method = results
        assert src_mod == 'fakemod'
        assert src_method is 'fakemethod'

    def test_import_settings(self, django_valid_conf):
        # Check that no settings found throws ImportError exception
        if 'django.conf' in sys.modules:
            del sys.modules['django.conf']
        with pytest.raises(ImportError):
            import_settings()

        # django framework
        sys.modules['django.conf'] = django_valid_conf
        src_mod, src_method = import_settings()
        assert src_mod == 'fakemod'
        assert src_method == 'fakemethod'

        # add tests for additional frameworks here #


def test_get_permissions_method(
        django_empty_conf,
        django_missing_src_module_conf,
        django_missing_src_method_conf,
        django_valid_conf,
        user_permission_single_mock
):
    # missing django.conf should throw an exception
    if 'django.conf' in sys.modules:
        del sys.modules['django.conf']
    with pytest.raises(Exception):
        get_permissions_method()

    # missing settings.GRAPHENE_FIELD_PERMISSION should throw exception
    sys.modules['django.conf'] = django_empty_conf
    with pytest.raises(Exception):
        get_permissions_method()

    # missing GRAPHENE_FIELD_PERMISSION.SRC_MODULE
    del sys.modules['django.conf']
    sys.modules['django.conf'] = django_missing_src_module_conf
    with pytest.raises(Exception):
        get_permissions_method()

    # test missing GRAPHENE_FIELD_PERMISSION.SRC_METHOD
    del sys.modules['django.conf']
    sys.modules['django.conf'] = django_missing_src_method_conf
    with pytest.raises(Exception):
        get_permissions_method()

    # valid django details but missing module+method
    del sys.modules['django.conf']
    if 'fakemod' in sys.modules:
        del sys.modules['fakemod']
    sys.modules['django.conf'] = django_valid_conf
    with pytest.raises(Exception):
        user_permissions_func = get_permissions_method()
        user_permissions_func()

    # the same valid django details but with module+method
    fakemod = Mock(spec=[])
    fakemod.fakemethod = Mock(return_value=user_permission_single_mock)
    sys.modules['fakemod'] = fakemod
    user_permissions_func = get_permissions_method()
    permission_list = user_permissions_func()

    assert 'permission1' in permission_list
    assert 'permission2' in permission_list
    assert 'permission3' in permission_list
