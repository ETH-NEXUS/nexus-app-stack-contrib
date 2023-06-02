from django.db.backends.postgresql import base

from django_udf_model.backends.postgresql.operations import DatabaseOperations


class DatabaseWrapper(base.DatabaseWrapper):
    ops_class = DatabaseOperations
