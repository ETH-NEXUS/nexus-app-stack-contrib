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

class Access:
    pass


class PrivateAccess(Access):
    pass


class GroupAccess(Access):
    def __init__(self, group_name=None):
        self.group_name = group_name


class AdminAccess(Access):
    pass


class NobodyAccess(Access):
    pass


PUBLIC_ACCESS = Access() # Default access - available to all
PRIVATE_ACCESS = PrivateAccess()
ADMIN_ACCESS = AdminAccess()
NOBODY_ACCESS = NobodyAccess()


def limit_access(field, access):
    assert not hasattr(field, "_access"), f"Field already has _access attribute: {field._access}"
    field._access = access
    return field


def get_field_access(field):
    access = getattr(field, "_access", PUBLIC_ACCESS)
    return access


def get_model_fields_by_access(model_class, access_type=None):
    result = []
    for field in model_class._meta.get_fields():
        if hasattr(field, "name"):  # Some virtual fields don't have names
            field_access = getattr(field, "_access", PUBLIC_ACCESS)
            if access_type is None or isinstance(field_access, access_type.__class__):
                result.append(field.name)
    return result
