# Code copied from https://gist.github.com/petrprikryl/7cd765cd723c7df983de03706bf27d1a

import re
from collections import OrderedDict
from typing import Any, Dict, Type, Optional
from typing import List

from django.db.models import ForeignObject
from django.db.models import QuerySet, Manager, NOT_PROVIDED, F, Model
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql import Query
from django.db.models.sql.datastructures import BaseTable, Join
from django.db.models.sql.where import WhereNode


class TableFunctionArg:
    def __init__(self, required: bool = True, default=NOT_PROVIDED):
        self.required = required  # type: bool
        self.default = default


class TableFunction(BaseTable):
    def __init__(self, table_name: str, alias: Optional[str], table_function_params: List[Any]):
        super().__init__(table_name, alias)
        self.table_function_params = table_function_params  # type: List[Any]

    def as_sql(self, compiler, connection):
        alias_str = '' if self.table_alias == self.table_name else (' %s' % self.table_alias)
        base_sql = compiler.quote_name_unless_alias(self.table_name)
        return '{}({}){}'.format(
            base_sql,
            ', '.join(['%s' for _ in range(len(self.table_function_params))]),
            alias_str
        ), self.table_function_params


class TableFunctionJoin(Join):
    def __init__(self, table_name, parent_alias, table_alias, join_type,
                 join_field, nullable, filtered_relation=None, table_function_params: List[Any] = None):
        super().__init__(table_name, parent_alias, table_alias, join_type,
                         join_field, nullable, filtered_relation)
        self.table_function_params = table_function_params  # type: List[Any]

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)
        if self.table_function_params is None:
            return sql, params  # normal table join

        # extract `on_clause_sql` from ancestor's complex compiled query logic
        # to be able pass function instead of normal table into sql easily
        # result = re.match('.+ join .+ on (?P<on_clause_sql>.+)', sql, re.IGNORECASE | re.DOTALL)
        # on_clause_sql = result.group('on_clause_sql')
        alias_and_on_clause_sql = sql[sql.find(" JOIN ") + 6:]

        table_function_placeholders = []
        table_function_params = []
        for param in self.table_function_params:
            if hasattr(param, 'as_sql'):
                param_sql, param_params = param.as_sql(compiler, connection)
            else:
                param_sql = '%s'
                param_params = [param]
            table_function_placeholders.append(param_sql)
            table_function_params += param_params

        sql = '{} {}({}) {}'.format(
            self.join_type,
            compiler.quote_name_unless_alias(self.table_name),
            ', '.join(table_function_placeholders),
            alias_and_on_clause_sql
        )
        return sql, table_function_params + params


class TableFunctionParams:
    def __init__(self, level: int, join_field: ForeignObject, params: 'OrderedDict[str, Any]'):
        self.level = level  # type: int
        self.join_field = join_field  # type: ForeignObject
        self.params = params  # type: OrderedDict[str, Any]


class TableFunctionQuery(Query):
    def __init__(self, model, where=WhereNode):
        super().__init__(model, where)
        self.table_function_params = []  # type: List[TableFunctionParams]

    def get_initial_alias(self):
        if self.alias_map:
            alias = self.base_table
            self.ref_alias(alias)
        else:
            if hasattr(self.model, 'function_args'):
                try:
                    params = list(
                        next(filter(lambda x: x.level == 0, self.table_function_params)).params.values()
                    )  # type: List[Any]
                except StopIteration:
                    # no parameters were passed from user
                    # so try to call the function without parameters
                    # in case that they are optional
                    params = []
                alias = self.join(TableFunction(self.get_meta().db_table, None, params))
            else:
                # TODO Why not call "super().get_initial_alias()" instead?
                alias = self.join(BaseTable(self.get_meta().db_table, None))
        return alias

    def setup_joins(self, names, opts, alias, can_reuse=None, allow_many=True,
                    reuse_with_filtered_relation=False):
        join_info = super().setup_joins(names, opts, alias, can_reuse, allow_many, reuse_with_filtered_relation)

        level = 0
        for alias in join_info.joins:
            join = self.alias_map[alias]
            if isinstance(join, TableFunction):
                continue  # skip the `FROM func(...)`, it is handled in `get_initial_alias`
            if not hasattr(join.join_field.related_model, 'function_args'):
                continue  # skip normal tables

            level += 1
            try:
                params = list(next(filter(
                    lambda x: x.level == level and x.join_field == join.join_field,
                    self.table_function_params
                )).params.values())  # type: List[Any]
            except StopIteration:
                # no parameters were passed from user
                # so try to call the function without parameters
                # in case that they are optional
                params = []

            resolved_params = []
            for param in params:
                if isinstance(param, F):
                    resolved_param = param.resolve_expression(self)
                else:
                    resolved_param = param
                resolved_params.append(resolved_param)

            self.alias_map[alias] = TableFunctionJoin(
                join.table_name, join.parent_alias, join.table_alias, join.join_type, join.join_field,
                join.nullable, join.filtered_relation, resolved_params
            )

        return join_info

    def table_function(self, **table_function_params: Dict[str, Any]):
        """
        Take user's passed params and store them in `self.table_function_params`
        to be prepared for joining.
        """
        _table_function_params = []
        for table_lookup, param_dict in self._table_function_params_to_groups(table_function_params).items():
            if not table_lookup:
                level = 0
                join_field = None
                model = self.model
            else:
                level = len(table_lookup.split(LOOKUP_SEP))
                lookup_parts, field_parts, _ = self.solve_lookup_type(table_lookup)
                path, final_field, targets, rest = self.names_to_path(
                    field_parts, self.get_meta(), allow_many=False, fail_on_missing=True
                )
                join_field = path[-1].join_field
                model = final_field.related_model

            _table_function_params.append(
                TableFunctionParams(
                    level=level, join_field=join_field,
                    params=self._reorder_table_function_params(model, param_dict)
                )
            )

        # TODO: merge with existing?
        self.table_function_params = _table_function_params

    def _table_function_params_to_groups(self, table_function_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transfer user specified lookups into groups
        to have all parameters for each table function prepared for joining.

        {id: 1, parent__id: 2, parent__code=3, parent__parent__id=4, root__id=5}
            =>
        {
            '': {'id': 1},
            'parent': {'id': 2, 'code': 3},
            'parent__parent': {'id': 4},
            'root': {'id: 5}
        }
        """
        param_groups = {}
        for lookup, val in table_function_params.items():
            parts = lookup.split(LOOKUP_SEP)
            prefix = LOOKUP_SEP.join(parts[:-1])
            field = parts[-1]
            if prefix not in param_groups:
                param_groups[prefix] = {}
            param_groups[prefix][field] = val
        return param_groups

    def _reorder_table_function_params(
        self, model: Type[Model], table_function_params: Dict[str, Any]
    ) -> 'OrderedDict[str, Any]':
        """
        Make sure that parameters will be passed into function in correct order.
        Also check required and set defaults.
        """
        ordered_function_params = OrderedDict()
        for key, arg in getattr(model, 'function_args').items():
            if key in table_function_params:
                ordered_function_params[key] = table_function_params[key]
            elif arg.default != NOT_PROVIDED:
                ordered_function_params[key] = arg.default
            elif arg.required:
                raise ValueError('Required function arg `{}` not specified'.format(key))

        remaining = set(table_function_params.keys()) - set(ordered_function_params.keys())
        if remaining:
            raise ValueError('Function arg `{}` not found'.format(remaining.pop()))

        return ordered_function_params


class TableFunctionQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self.query = query or TableFunctionQuery(self.model)

    def table_function(self, **table_function_params: Dict[str, Any]) -> 'TableFunctionQuerySet':
        self.query.table_function(**table_function_params)
        return self

    def _update(self, values):
        return super()._update(values)


class TableFunctionManager(Manager):
    def get_queryset(self) -> TableFunctionQuerySet:
        return TableFunctionQuerySet(model=self.model, using=self._db, hints=self._hints)
