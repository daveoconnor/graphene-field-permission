import logging
import pytest
from unittest.mock import MagicMock, Mock
import graphene_field_permission

single_permission_data = ['permission1', 'permission2', 'permission3']
group_permission_data = {
    'group-1234': ['permission1', 'permission2', 'permission3'],
    'group-5678': ['permission4', 'permission5', 'permission6'],
}
structured_single_permission_data = {
    'permission1': True,
    'permission2': True,
    'permission3': True,
}
structured_group_permission_data = {
    'group-1234': {
        'permission1': True,
        'permission2': True,
        'permission3': True,
    },
    'group-5678': {
        'permission4': True,
        'permission5': True,
        'permission6': True,
    }
}

@pytest.fixture
def single_info():
    info = MagicMock()
    info.context.user_permissions = structured_single_permission_data
    return info


@pytest.fixture
def group_info():
    info = MagicMock()
    info.context.user_permissions = structured_group_permission_data
    return info


@pytest.fixture
def info_context_mock():
    context = Mock(spec=[])
    context.user = Mock()
    return context


@pytest.fixture
def info_mock():
    info = Mock(spec=[])
    info.context = Mock(spec=[])
    info.context.user = Mock()
    return info


@pytest.fixture
def logger():
    return logging.getLogger('graphene_field_permission.permissions')


@pytest.fixture
def fetch_permissions_single_permissions(monkeypatch):
    monkeypatch.setattr(
        graphene_field_permission.api,
        "fetch_permissions",
        Mock(return_value=structured_single_permission_data),
    )


@pytest.fixture
def django_empty_conf():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    return django_mock


@pytest.fixture
def django_missing_src_module_conf():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {}
    return django_mock


@pytest.fixture
def django_missing_src_method_conf():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
        'SRC_MODULE': 'fakemod'
    }
    return django_mock


@pytest.fixture
def django_valid_conf():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
        'SRC_MODULE': 'fakemod',
        'SRC_METHOD': 'fakemethod'
    }
    return django_mock


@pytest.fixture
def orm_data_mock():
    test_data = Mock()
    test_data.name = 'foobar'
    test_data.group.corporation.id = 'group-5678'
    return test_data


@pytest.fixture
def user_permission_single_mock(user=None):
    return single_permission_data


@pytest.fixture
def user_permission_group_mock(user=None):
    return group_permission_data


@pytest.fixture
def single_permissions(monkeypatch):
    def get_permissions_method():
        return Mock(return_value=single_permission_data)

    monkeypatch.setattr(
        graphene_field_permission.permissions_loader,
        "get_permissions_method",
        get_permissions_method,
    )


@pytest.fixture
def group_permissions(monkeypatch):
    def get_permissions_method():
        return Mock(return_value=group_permission_data)

    monkeypatch.setattr(
        graphene_field_permission.permissions_loader,
        "get_permissions_method",
        get_permissions_method,
    )
