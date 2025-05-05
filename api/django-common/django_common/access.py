"""
Field-level access control for Django models.

This module provides a mechanism to define access control at the field level.

Usage:
    from django_common.access import ADMIN_ACCESS, GroupAccess, limit_access, NOBODY_ACCESS, PRIVATE_ACCESS

    class MyModel(models.Model):
        # Public field - accessible to all users (default)
        public_field = models.CharField(max_length=100)
        
        # Private field - only accessible to the owner of the object
        private_field = limit_access(models.CharField(max_length=100), PRIVATE_ACCESS)
        
        # Admin field - only accessible to administrators
        admin_field = limit_access(models.CharField(max_length=100), ADMIN_ACCESS)
        
        # Group field - only accessible to users in the specified group
        group_field = limit_access(models.CharField(max_length=100), GroupAccess("group_name"))

        # Foreign key field - nobody is allowed to access it
        other_model = limit_access(models.ForeignKey(OtherModel), NOBODY_ACCESS)

    # Get all fields with a specific access type
    private_fields = get_model_fields_by_access(MyModel, Private)
    
    # Get access type for a specific field
    field = MyModel._meta.get_field("private_field")
    access = get_field_access(field)
"""

class _Access:
    def __str__(self):
        return "PUBLIC_ACCESS"


class _PrivateAccess(_Access):
    def __str__(self):
        return "PRIVATE_ACCESS"


class _AdminAccess(_Access):
    def __str__(self):
        return "ADMIN_ACCESS"


class _NobodyAccess(_Access):
    def __str__(self):
        return "NOBODY_ACCESS"


class GroupAccess(_Access):
    def __init__(self, group_name=None):
        self.group_name = group_name

    def __str__(self):
        raise NotImplementedError


PUBLIC_ACCESS = _Access() # Default access - available to all
PRIVATE_ACCESS = _PrivateAccess()
ADMIN_ACCESS = _AdminAccess()
NOBODY_ACCESS = _NobodyAccess()


def _get_access_object(string):
    match string:
        case "PUBLIC_ACCESS":
            return PUBLIC_ACCESS
        case "PRIVATE_ACCESS":
            return PRIVATE_ACCESS
        case "ADMIN_ACCESS":
            return ADMIN_ACCESS
        case "NOBODY_ACCESS":
            return NOBODY_ACCESS
    raise NotImplementedError()


def limit_access(field, access):
    assert not hasattr(field, "_access"), f"Field already has _access attribute: {field._access}"
    field._access = access
    return field


def _get_field_access(field):
    access = getattr(field, "_access", PUBLIC_ACCESS)
    return access


def _is_authenticated(request):
    return request.user.is_authenticated


def _is_admin(request):
    return _is_authenticated(request) and request.user.is_staff


def _has_access(access, request):
    assert access and request
    if type(access) == _Access:
        return True
    elif type(access) == _PrivateAccess and _is_authenticated(request):
        return True
    elif type(access) == _AdminAccess and _is_admin(request):
        return True
    elif (type(access) == GroupAccess and _is_authenticated(request)
          and request.user.groups.filter(name=access.group_name).exists()):
        return True
    return False


def _is_authentication_required(access):
    return type(access) in (_PrivateAccess, _AdminAccess, GroupAccess)


def get_model_fields_by_access(model_class, access_type=None):
    result = []
    for field in model_class._meta.get_fields():
        if hasattr(field, "name"):  # Some virtual fields don't have names
            field_access = getattr(field, "_access", PUBLIC_ACCESS)
            if access_type is None or isinstance(field_access, access_type.__class__):
                result.append(field.name)
    return result
