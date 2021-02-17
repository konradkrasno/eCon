from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.production.custom_registry.registry import Registry, Function


class CreateTableForm(FlaskForm):
    table_name = StringField("Table Name", validators=[DataRequired()])
    submit = SubmitField("Create")

    def __init__(self, invest_id: int, username: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invest_id = invest_id
        self.username = username
        self.registry = None

    def validate_table_name(self, table_name):
        try:
            self.registry = Registry(self.invest_id, self.username, table_name.data)
        except ValueError as e:
            raise ValidationError(e.__str__())


class AddColumnForm(FlaskForm):
    name = StringField("Column Name", validators=[DataRequired()])
    data_type = SelectField("Data Type", choices=["string", "integer", "float", "bool"])
    submit = SubmitField("Create")

    def __init__(
        self, invest_id: int, username: str, registry_name: str, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.registry = Registry(invest_id, username, registry_name)

    def validate_name(self, name):
        if name.data in self.registry.get_fields():
            raise ValidationError("Field with this name already exits.")


class AddFunctionForm(FlaskForm):
    first_field = SelectField("First Field")
    second_field = SelectField("Second Field")
    operator = SelectField("Choose Operator")
    func_field_name = StringField("New Field Name", validators=[DataRequired()])
    submit = SubmitField("Create")

    def __init__(
        self, invest_id: int, username: str, registry_name: str, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.registry = Registry(invest_id, username, registry_name)
        self.first_field.choices = self.registry.get_fields(numeric_fields=True)
        self.second_field.choices = self.registry.get_fields(numeric_fields=True)
        self.operator.choices = Function.operators()
