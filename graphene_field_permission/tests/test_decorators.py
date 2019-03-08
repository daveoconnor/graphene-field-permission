import pytest
from graphene_field_permission.decorators import has_field_access
from unittest.mock import Mock, MagicMock


@pytest.fixture
def group_permissions():
    return {
        'group-1234': [
            'permission1',
            'permission2',
            'permission3',
        ],
        'group-5678': [
            'permission4',
            'permission5',
            'permission6',
        ]
    }


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
def singleinfo():
    info = MagicMock()
    info.context.user_permissions = [
        'permission1',
        'permission2',
        'permission3',
    ]
    return info


@pytest.fixture(autouse=True)
def groupinfo(group_permissions):
    info = MagicMock()
    info.context.user_permissions = group_permissions
    return info


class TestDecorators():
    def test___init__(self, decorator1, decorator2, decorator3):
        assert 'permission1' in decorator1.req_perms
        assert decorator1.filter_field is None
        assert 'permission2' in decorator2.req_perms
        assert 'permission3' in decorator2.req_perms
        assert decorator2.filter_field == 'id'
        assert 'permission4' in decorator3.req_perms
        assert 'permission5' in decorator3.req_perms
        assert decorator3.filter_field == 'division.corporation.id'

    def test__permissions_filter(self, decorator1, decorator2, decorator3,
                                 group_permissions):

        permissions = has_field_access._permissions_filter(
            decorator1,
            group_permissions,
            'group-1234'
        )
        assert 'permission1' in permissions
        assert 'permission2' in permissions
        assert 'permission3' in permissions
        assert 'permission4' not in permissions
        assert 'permission5' not in permissions
        assert 'permission6' not in permissions

        permissions2 = has_field_access._permissions_filter(
            decorator1,
            group_permissions,
            'group-5678'
        )
        assert 'permission1' not in permissions2
        assert 'permission2' not in permissions2
        assert 'permission3' not in permissions2
        assert 'permission4' in permissions2
        assert 'permission5' in permissions2
        assert 'permission6' in permissions2

        # test that an exception is raised on incorrect key access
        with pytest.raises(Exception):
            has_field_access._permissions_filter(
                decorator1,
                group_permissions,
                'group-NONE'
            )

    def test__get_filter_data(self, decorator1, decorator2, decorator3):
        # test a single level
        test_data = Mock()
        test_data.id = 'foo'
        assert has_field_access._get_filter_data(
            decorator3,
            test_data,
            'id'
        ) == 'foo'

        # test multiple levels
        test_data = Mock()
        test_data.group.division.corporation.id = 'foo'
        assert has_field_access._get_filter_data(
            decorator3,
            test_data,
            'group.division.corporation.id'
        ) == 'foo'
        # test missing relation works
        with pytest.raises(Exception):
            # test multiple levels
            has_field_access._get_filter_data(
                decorator3,
                {},
                'two.steps.beyond'
            )

    def test__has_access(self, decorator1, decorator2, decorator3,
                         group_permissions):
        assert decorator1._has_access(['permission1']) is True
        # test that it's OR
        assert decorator1._has_access(['permission1', 'permX']) is True
        # test that order doesn't matter
        assert decorator1._has_access(['permX', 'permission1']) is True
        assert decorator1._has_access(['permX']) is False

        assert decorator2._has_access(
            group_permissions,
            'group-1234'
        ) is True
        # test for false positive
        assert decorator2._has_access(
            group_permissions,
            'group-5678'
        ) is False

        assert decorator3._has_access(
            group_permissions,
            'group-5678'
        ) is True
        # test for false positive
        assert decorator3._has_access(
            group_permissions,
            'group-1234'
        ) is False

    def test___call__(self, singleinfo, groupinfo):
        # test working group
        @has_field_access('permission4', filter_field='group.corporation.id')
        def resolve_testfield(test_data, info):
            assert test_data.name == 'foobar'

        test_data = Mock()
        test_data.name = 'foobar'
        test_data.group.corporation.id = 'group-5678'
        resolve_testfield(test_data, groupinfo)

        # test one to failing
        @has_field_access('permissionX')
        def resolve_testfield(test_data, info):
            pass

        with pytest.raises(Exception):
            resolve_testfield({}, singleinfo)

        # test failing group
        @has_field_access('permission3', filter_field='group.corporation.id')
        def resolve_testfield(test_data, info):
            assert test_data.name == 'foobar'

        with pytest.raises(Exception):
            test_data = Mock()
            test_data.name = 'foobar'
            test_data.group.corporation.id = 'group-5678'
            resolve_testfield(test_data, groupinfo)
