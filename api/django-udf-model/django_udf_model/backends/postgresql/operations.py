from django.db.backends.postgresql import operations


class DatabaseOperations(operations.DatabaseOperations):
    compiler_module = 'django_udf_model.backends.postgresql.compiler'
