from unittest.mock import Mock
import logging

# django conf mocks


def django_empty_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    return django_mock


def django_missing_src_module_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {}
    return django_mock


def django_missing_src_method_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
        'SRC_MODULE': 'fakemod'
    }
    return django_mock


def django_valid_conf_mock():
    django_mock = Mock(spec=[])
    django_mock.settings = Mock(spec=[])
    django_mock.settings.GRAPHENE_FIELD_PERMISSION = {
        'SRC_MODULE': 'fakemod',
        'SRC_METHOD': 'fakemethod'
    }
    return django_mock


def user_permission_single_mock(user=None):
    return ['permission1', 'permission2', 'permission3']


def user_permission_group_mock(user=None):
    return {
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


def logger_mock():
    return logging.getLogger('graphene_field_permission.permissions')

def orm_data_mock():
    test_data = Mock()
    test_data.name = 'foobar'
    test_data.group.corporation.id = 'group-5678'
    return test_data