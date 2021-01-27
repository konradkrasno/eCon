from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class CreateTableForm(FlaskForm):
    table_name = StringField("Table Name", validators=[DataRequired()])
    submit = SubmitField("Create")


class CreateColumnForm(FlaskForm):
    column_name = StringField("Column Name", validators=[DataRequired()])
    data_type = SelectField("Data Type", choices=["string", "integer", "float", "bool"])
    submit = SubmitField("Create")
