from django.db.backends.postgresql import base, features

from django_udf_model.backends.postgresql.operations import DatabaseOperations


class DatabaseFeatures(features.DatabaseFeatures):
    # Disabled because PostgreSQL does not support this for UDF results.
    allows_group_by_selected_pks = False


class DatabaseWrapper(base.DatabaseWrapper):
    features_class = DatabaseFeatures
    ops_class = DatabaseOperations
