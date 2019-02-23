# Graphene Field Permission

A package to add field-level permissions for [graphene-django](https://github.com/graphql-python/graphene-django).



## Use
On schema nodes add a decorator "\@has_field_access" to a resolve for each field that you want checked.


Usage Example:
```
from graphene_field_permission.decorators import has_field_access

class GroupNode(DjangoObjectType):
    @has_field_access('permission1')
    def resolve_group_name(self, info):
        return self.name

    # example showing checking for one of multiple (unlimited) permissions
    @has_field_access('permission1', 'permission2')
    def resolve_group_description(self, info):
        return self.description

    # example showing checking for one of multiple (unlimited) permissions
    @has_field_access('permission1', 'permission2', filter_id='group-id-123')
    def resolve_group_description(self, info):
        return self.description

    class Meta:
        model = Group
        ...

```

### Usage notes:

1. An exception is thrown should a user attempt to access a field for which they don't have access. Graphene-django doesn't allow returning None for fields which aren't set as nullable. That makes it necessary to have your graphql queries to be fine grained enough to not call those fields in the first place. Client side checking of permissions is recommended in order to limit the field's accessed in the query in the first place.
1. I tried about four different ways to do this so resolve_field wasn't necessary, but found this to be the best balance between making it schema-definable and performant. I'm open to pull requests if someone can think of a better way.

## Setup

After setting up graphene following its own instructions.


1. Create a file that will return a struct of permissions allowed for the user. By default arrays and dicts containing arrays are supported. However that functionality can be extended by the user fairly easily by using your own "has_field_access" decorator

Example:

app/helpers/user_permissions.py

```
# standard version
def get_user_permissions(user):
    # query database to determine the passed in user's permissions
    return ['permission1', 'permission2', 'permission3']

# filter_id utilising version
def get_user_permissions(user):
    # query database to determine the passed in user's permissions
    return {
        'group-id-123': ['permission1', 'permission2', 'permission3'],
        'group-id-456': ['permission1', 'permission3', 'permission5'],
    }
```

Update settings.py to add:

```
GRAPHENE = {
    'MIDDLEWARE': [
        'config.schema.middleware.permissions.PermissionsMiddleware',
    ]

}

GRAPHENE_FIELD_PERMISSION = {
    'SRC_MODULE': 'app.helpers.user_permissions',
    'SRC_METHOD': 'get_user_permissions',
}
```

## Future updates, notes

I don't plan to develop this a whole lot further. It has scratched my itch for now. I would like to add the following though:

1. Unit tests, may get added in time
1. This currently only supports Graphene under Django. I'm open to others adding support for other graphene-python projects if they want to submit pull requests.
