import pytest
from graphene_field_permission import api
from graphene_field_permission.decorators import has_field_access

from .fixtures import (
    single_info,
    group_info,
    orm_data_mock,
    user_permission_group_mock,


@pytest.fixture
def decorator1():
    # simple permission check
    yield has_field_access(
        'permission1'
    )


@pytest.fixture
def decorator2():
    # filter group by data object field
    yield has_field_access(
        'permission2',
        'permission3',
        filter_field='id',
    )


@pytest.fixture
def decorator3():
    yield has_field_access(
        'permission4',
        'permission5',
        filter_field='division.corporation.id',
    )


class TestDecorators:
    def test___init__(self, decorator1, decorator2, decorator3):
        assert 'permission1' in decorator1.req_perms
        assert decorator1.filter_field is None
        assert 'permission2' in decorator2.req_perms
        assert 'permission3' in decorator2.req_perms
        assert decorator2.filter_field == 'id'
        assert 'permission4' in decorator3.req_perms
        assert 'permission5' in decorator3.req_perms
        assert decorator3.filter_field == 'division.corporation.id'

    def test___call__(self, single_info, group_info, orm_data_mock, monkeypatch):
        def patch_field_access(*requirements, info_context, filter_field, filter_data):
            return True

        def patch_field_access_fail(*requirements, info_context, filter_field, filter_data):
            raise PermissionError

        with monkeypatch.context() as m:
            m.setattr(
                api,
                'check_field_access',
                patch_field_access
            )

            # test working group
            @has_field_access('permission4', filter_field='group.corporation.id')
            def resolve_testfield(test_data, info):
                assert test_data.name == 'foobar'

            resolve_testfield(orm_data_mock, group_info)

        with monkeypatch.context() as m:
            monkeypatch.setattr(
                api,
                'check_field_access',
                patch_field_access_fail
            )

            # test one to failing
            @has_field_access('permissionX')
            def resolve_testfield(test_data, info):
                pass

            with pytest.raises(Exception):
                resolve_testfield({}, single_info)

            # test failing group
            @has_field_access('permission3', filter_field='group.corporation.id')
            def resolve_testfield(test_data, info):
                assert test_data.name == 'foobar'

            with pytest.raises(Exception):
                resolve_testfield(orm_data_mock, group_info)
