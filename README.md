# Graphene Field Permission

A package to add field-level permissions for [Graphene Python](https://graphene-python.org/). 

Currently only supports Django/[Graphene Django](https://github.com/graphql-python/graphene-django) but would welcome pull requests adding support for other ORMs.


## Usage

### Queries
On schema nodes add the decorator ```@has_field_access``` to the resolve for any field that you want checked.

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

Example showing checking for one of multiple permissions under a group, for cases where permissions differ by group id:

```python
from graphene_field_permission.decorators import has_field_access

class GroupNode(DjangoObjectType):
    @has_field_access('permission1', 'permission2', filter_field='group_id')
    def resolve_group_text(self, info):
        return self.text
```
#### filter_field 
A ```filter_field``` value of 'group_id' in the above example will look at the GroupNode group_id field. Add ```.``` separators for related objects.

```filter_field``` processing will traverse related objects as necessary to reduce the number of queries.

It's recommended to try and reduce these as much as possible. e.g. using group.division.corporation_id instead of group.division.corporation.id

```python
@has_field_access('permission1', 'permission2', filter_field='group.division.corporation_id')
```

### Mutations

Add ```check_field_access()``` call for the permission you want to confirm - one check per mutation will work. Raises PermissionError if no match found. Permission arguments are logical OR.

```python
from graphene_field_permission import check_field_access

class ModifyGroup(graphene.Mutation):
     # Normal mutation setup here...
    
    def mutate(self, info, id, field_1_data, field_2_data):
        d = ORM.objects.find(pk=id)
        d.field_1 = field_1_data
        # checking of permissions:
        try:
            check_field_access('permission1', info_context=info.context)
            d.protected_field = field_2_data
        except PermissionError as exc1:
            raise Exception from exc1        
        d.save()
        
```

Grouped permissions

```python
from graphene_field_permission import check_field_access

class ModifyGroup(graphene.Mutation):
     # Normal mutation setup here...
    
    def mutate(self, info, id, field_1_data, field_2_data):
        fd = ModelName.objects.find(pk=id)
        fd.field_1 = field_1_data
        # checking of permissions:
        try:
            # check for user having permission1 OR permission2
            check_field_access(
                'permission1',
                'permission2',
                filter_field='group.division.corporation_id',
                filter_data=fd,
                info_context=info.context,                
            )
            fd.protected_field = field_2_data
        except PermissionError as exc1:
            raise Exception from exc1        
        fd.save()
        
```
```filter_field``` along with ```filter_data``` works the same way as ```filter_field``` does in queries, with ```filter_data``` providing the ORM object to be traversed.

More than one ```check_field_access()``` call can be made and retrieved permissions will be retained between the calls.

## Sample Result in GraphQL output from query decorator:

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
    "group": {
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

1. An exception is thrown should a user attempt to access a field for which they don't have access. the reason for this is that graphene-django doesn't allow returning ```None``` for fields which aren't set as nullable so this is the best way of proceeding and follows that convention throughout. That makes it necessary to have your graphql queries fine grained enough to not call those fields in the first place. 
    1. Client side checking of permissions is recommended in order to limit the field's accessed in the query in the first place.


## Installation

```
pip install graphene-field-permission
```

## Setup

1. Set up graphene and graphene django following their own instructions.
1. Create a module and method that will return permissions allowed for the user as shown below. By default lists and dicts containing lists are supported.
1. Update settings.py to match the instructions below.

### Example permissions resolution
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

#### User Permission Call Information

1. These get called once per graphql query call. 
1. It's recommended to use the logs to try to minimise the number of queries generated by this function. Ideally it would be best to do it in a single query.
1. It's recommended to use Django ORM's ```select_related``` on queries where necessary in order to minimise the number of queries.

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

## Future updates, design notes

1. I don't plan to develop this a whole lot further. It has scratched my itch for now. 
1. I tried about four different ways to do this so resolve_field wasn't necessary, but found this to be the best balance of making it schema-definable and performant. I'm open to pull requests if someone can think of a better way.
1. This currently only supports Graphene under Django. I'm open to others adding support for other graphene-python projects if they want to submit pull requests.
