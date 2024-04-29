from contextlib import contextmanager
from django.db import transaction
from django.db.transaction import get_connection


# Code copied from https://stackoverflow.com/questions/19686204/django-orm-and-locking-table#54403001
# See also https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-TABLES
# Ensures that the order of row identifiers matches the insertion order.
@contextmanager
def exclusive_insert_table_lock(model):
    with transaction.atomic():
        cursor = get_connection().cursor()
        cursor.execute(f"LOCK TABLE {model._meta.db_table} IN SHARE MODE")
        try:
            yield
        finally:
            cursor.close()
