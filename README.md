# Graphene Field Permission

A package to add field-level permissions for [graphene-django](https://github.com/graphql-python/graphene-django).


## Use
On schema nodes add a decorator "\@has_field_access" to a resolve for each field that you want checked.


Usage example in schema files:
```python
from graphene_field_permission.decorators import has_field_access

class GroupNode(DjangoObjectType):
    @has_field_access('permission1')
    def resolve_group_name(self, info):
        return self.name

    class Meta:
        model = Group
        ...
```

Example showing checking for one of multiple (unlimited) permissions:

```python
from graphene_field_permission.decorators import has_field_access

class GroupNode(DjangoObjectType):
    @has_field_access('permission1', 'permission2')
    def resolve_group_description(self, info):
        return self.description
```

Example showing checking for one of multiple permissions under a group, for cases where permissions differ by group:

```python
from graphene_field_permission.decorators import has_field_access

class GroupNode(DjangoObjectType):
    @has_field_access('permission1', 'permission2', filter_id='group-id-123')
    def resolve_group_text(self, info):
        return self.text


```

## Result in GraphQL output:

```javascript
{
  "errors": [
    {
      "message": "No access for user on field 'group_name'",
      "locations": [
        {
          "line": 7,
          "column": 9
        }
      ],
      "path": [
        "group",
        "edges",
        0,
        "node",
        "groupName"
      ]
    }
  ],
  "data": {
    "team": {
      "edges": [
        {
          "node": null
        }
      ]
    }
  }
}
```

### Usage notes:

1. An exception is thrown should a user attempt to access a field for which they don't have access. Graphene-django doesn't allow returning None for fields which aren't set as nullable. That makes it necessary to have your graphql queries fine grained enough to not call those fields in the first place. Client side checking of permissions is recommended in order to limit the field's accessed in the query in the first place.
1. I tried about four different ways to do this so resolve_field wasn't necessary, but found this to be the best balance of making it schema-definable and performant. I'm open to pull requests if someone can think of a better way.


## Installation

```
pip install graphene-field-permission
```

## Setup

1. Set up graphene and graphene django following their own instructions.
1. Create a file that will return permissions allowed for the user as shown below. By default lists and dicts containing lists are supported. That capability can be overridden by the user fairly easily by using your own "has_field_access" decorator and any data structure you prefer.
1. Update settings.py to match the instructions below.

### Example permissions population

These get called once per graphql call. Recommended to use Django ORM's ```select_related``` on queries where necessary in order to minimise the number of queries.

Standard:

```python
def get_user_permissions(user):
    # query database to determine the passed in user's permissions
    return ['permission1', 'permission2', 'permission3']

```

Or grouped:

```python
def get_user_permissions(user):
    # query database to determine the passed in user's permissions
    return {
        'group-id-123': ['permission1', 'permission2', 'permission3'],
        'group-id-456': ['permission1', 'permission3', 'permission5'],
    }
```

### Settings

With the above method at app/helpers/user_permissions.py (for example) update settings.py to add:

```python
GRAPHENE_FIELD_PERMISSION = {
    'SRC_MODULE': 'app.helpers.user_permissions',
    'SRC_METHOD': 'get_user_permissions',
}
```

Also update the main graphene settings to add the middleware.


```python
GRAPHENE = {
    'MIDDLEWARE': [
        'graphene_field_permission.permissions.PermissionsMiddleware'
    ]
}
```

## Future updates, notes

I don't plan to develop this a whole lot further. It has scratched my itch for now. I would like to add the following though:

1. Unit tests, may get added in time.
1. This currently only supports Graphene under Django. I'm open to others adding support for other graphene-python projects if they want to submit pull requests.
