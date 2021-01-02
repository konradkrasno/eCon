from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired


class InvestmentForm(FlaskForm):
    name = StringField("Investment Name", validators=[DataRequired()])
    description = TextAreaField("Investment Description")
    submit = SubmitField("Create")
