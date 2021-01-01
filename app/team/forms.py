from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email


class CreateWorkerForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    position = StringField("Position", validators=[DataRequired()])
    admin = BooleanField("Root Permission")
    submit = SubmitField("Create")


class EditWorkerForm(FlaskForm):
    position = StringField("Position", validators=[DataRequired()])
    submit = SubmitField("Create")
