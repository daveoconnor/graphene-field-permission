import logging
import pytest
from unittest.mock import MagicMock, Mock
from graphene_field_permission.decorators import has_field_access
from .mocks import orm_data_mock, user_permission_group_mock


@pytest.fixture(scope='module')
def decorator1():
    # simple permission check
    yield has_field_access(
        'permission1'
    )


@pytest.fixture(scope='module')
def decorator2():
    # filter group by data object field
    yield has_field_access(
        'permission2',
        'permission3',
        filter_field='id',
    )


@pytest.fixture(scope='module')
def decorator3():
    yield has_field_access(
        'permission4',
        'permission5',
        filter_field='division.corporation.id',
    )


@pytest.fixture(autouse=True)
def single_info():
    info = MagicMock()
    info.context.user_permissions = {
        'permission1': True,
        'permission2': True,
        'permission3': True,
    }
    return info


@pytest.fixture(autouse=True)
def group_info():
    info = MagicMock()
    info.context.user_permissions = user_permission_group_mock
    return info


@pytest.fixture
def test_data():
    return orm_data_mock()


@pytest.fixture
def logger():
    return logging.getLogger('graphene_field_permission.permissions')


@pytest.fixture
def user():
    return Mock()


@pytest.fixture
def django_mock():
    return django_empty_conf_mock()


def django_empty_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    return django_mock


@pytest.fixture
def django_valid_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
        'SRC_MODULE': 'fakemod',
        'SRC_METHOD': 'fakemethod'
    }
    return django_mock
