from django.db import models
from django.db import connection
from django.db.backends.ddl_references import Statement, Table
from django.db.models.constraints import UniqueConstraint


class IUniqueConstraint(UniqueConstraint):
    def constraint_sql(self, model, schema_editor) -> str:
        return self.create_sql(model, schema_editor)

    def create_sql(self, model, schema_editor) -> str:
        fields = [
            model._meta.get_field(field_name).column
            for field_name in self.fields
        ]
        condition = self._get_condition_sql(model, schema_editor)  # type: ignore
        if condition and not connection.features.support_partial_indexes:
            return ''
        table = Table(model._meta.db_table, schema_editor.quote_name)
        name = schema_editor.quote_name(self.name)
        columns = ", ".join(
            map(
                lambda x: f"LOWER({schema_editor.quote_name(x)})",
                fields
            )
        )
        statement = Statement(
            schema_editor.sql_create_unique_index,
            table=table,
            name=name,
            columns=columns,
            condition=schema_editor._index_condition_sql(condition),
            deferrable=schema_editor._deferrable_constraint_sql(None),
            include=schema_editor._index_include_sql(model, None),
        )
        if not hasattr(schema_editor, 'deferred_sql'):
            schema_editor.deferred_sql = []
        schema_editor.deferred_sql.append(statement)
        return ''

