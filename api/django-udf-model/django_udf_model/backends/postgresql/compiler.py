from django.core.exceptions import FullResultSet
from django.db.models import Subquery
from django.db.models.fields.related_lookups import RelatedIn
from django.db.models.sql import compiler

from django_udf_model import Command


def complete_sql(command, c, fields_and_values, values, update_params):
    qn = c.quote_name_unless_alias

    for field, model, val in fields_and_values:
        val = field.get_db_prep_save(val, connection=c.connection)

        # Getting the placeholder for the field.
        if hasattr(field, "get_placeholder"):
            placeholder = field.get_placeholder(val, c, c.connection)
        else:
            placeholder = "%s"
        name = field.column
        if hasattr(val, "as_sql"):
            sql, params = c.compile(val)
            values.append("%s => %s" % (qn(name), placeholder % sql))
            update_params.extend(params)
        elif val is not None:
            values.append("%s => %s" % (qn(name), placeholder))
            update_params.append(val)
        else:
            values.append("%s => NULL" % qn(name))

    opts = c.query.get_meta()
    table = opts.db_table
    result = [
        'SELECT %s_%s' % (command, table), '(', ', '.join(values), ')'
    ]
    return ''.join(result), tuple(update_params)


class SQLCompiler(compiler.SQLCompiler):
    pass


class SQLInsertCompiler(compiler.SQLInsertCompiler):

    def as_sql(self):
        values, update_params = [], []

        if len(self.query.objs) > 1:
            raise 'Not supported'

        if self.query.fields:
            opts = self.query.get_meta()
            fields = self.query.fields or [opts.pk]
            value_rows = [
                self.prepare_value(field, self.pre_save_val(field, self.query.objs[0]))
                for field in fields
            ]
        else:
            value_rows = [self.connection.ops.pk_default_value()]
            fields = [None]

        return [complete_sql(Command.INSERT.value, self, zip(fields, [self.query.model for _ in fields], value_rows),
                             values, update_params)]


class SQLUpdateCompiler(compiler.SQLUpdateCompiler):

    def as_sql(self):
        if not self.query.values:
            return '', ()

        values, update_params = [], []

        try:
            if len(self.query.where.children) > 0:
                rhs_sql, rhs_params = self.query.where.children[0].process_rhs(self, self.connection)
                values.append('id => %s' % rhs_sql)
                update_params.append(rhs_params[0])
        except FullResultSet:
            pass

        return complete_sql(Command.UPDATE.value, self, self.query.values, values, update_params)


class SQLDeleteCompiler(compiler.SQLDeleteCompiler):

    def _as_sql(self, query):
        try:
            rhs_sql, rhs_params = query.where.children[0].process_rhs(self, self.connection)
            if isinstance(query.where.children[0].rhs, Subquery):
                rhs_sql = f'(VARIADIC array{rhs_sql})'
        except FullResultSet:
            rhs_sql = '()'
            rhs_params = ()
        if isinstance(query.where.children[0], RelatedIn):
            qn = self.quote_name_unless_alias
            rhs_sql = '__related(VARIADIC %s => %s)' % (qn(query.where.children[0].lhs.target.column + 's'), '%s')
            params = (list(rhs_params),)
        else:
            params = tuple(rhs_params)

        return 'SELECT %s_%s%s' % (Command.DELETE.value, query.base_table, rhs_sql), params
