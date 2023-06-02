========================================
Django User-Defined Function (UDF) Model
========================================

Django UDF allows model objects to be based on UDFs.

Setup
=====

An additional database connection and router is required:

.. code-block:: python
 DATABASES = {
     'udf': {
         'ENGINE': 'django_udf_model.backends.postgresql',
         'HOST': environ.get('DJANGO_POSTGRES_HOST'),
         'PORT': environ.get('DJANGO_POSTGRES_PORT'),
         'NAME': environ.get('DJANGO_POSTGRES_DB'),
         'USER': environ.get('DJANGO_POSTGRES_USER'),
         'PASSWORD': environ.get('DJANGO_POSTGRES_PASSWORD'),
     }
 }

 DATABASE_ROUTERS = ("django_udf_model.models.UdfConnectionRouter",)

Define a model class with the extra attributes ``function_args``, ``objects``, ``using``, ``db_table`` and ``managed``:

.. code-block:: python
 from collections import OrderedDict
 from django.db.models import CharField, Model
 from django_udf_model.query import TableFunctionManager

 class Foo(Model):
     function_args = OrderedDict()
     objects = TableFunctionManager()
     using = 'udf'

     bar = CharField(max_length=128)

     class Meta:
         db_table = 'foo'
         managed = False

The attribute ``using`` defines the responsible database connection and ``db_table`` the naming on the database side.
Accessing such model objects results in queries like ``SELECT insert_foo(1, 'baz')``, ``SELECT * FROM select_foo()``,
``SELECT update_foo(1, 'zab')`` and ``SELECT * FROM delete_foo(1)``. These functions must be defined manually:

.. code-block:: sql
 CREATE TABLE foo (
   id SERIAL4 PRIMARY KEY,
   bar TEXT NOT NULL
 );

 CREATE FUNCTION insert_foo(bar TEXT) RETURNS INT4 AS $$
   INSERT INTO foo (bar) VALUES ($1) RETURNING foo.id;
 $$ LANGUAGE SQL;

 CREATE FUNCTION select_foo() RETURNS SETOF foo AS $$
   SELECT * FROM foo;
 $$ LANGUAGE SQL;

 CREATE FUNCTION update_foo(id INT4, bar TEXT) RETURNS VOID AS $$
   UPDATE foo SET bar = $2 WHERE foo.id = $1
 $$ LANGUAGE SQL;

 CREATE FUNCTION delete_foo(id INT4) RETURNS VOID AS $$
   DELETE FROM foo WHERE foo.id = $1;
 $$ LANGUAGE SQL;

  ALTER TABLE foo OWNER TO django;


Using
=====

For example, now this model is fully accessible from the admin site:

.. code-block:: python
 from django.contrib import admin
 from models import Foo

 @admin.register(Foo)
 class SourceConfigAdmin(admin.ModelAdmin):
     pass
