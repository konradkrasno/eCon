from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, ValidationError
from app.models import Investment


class InvestmentForm(FlaskForm):
    name = StringField("Investment Name", validators=[DataRequired()])
    description = TextAreaField("Investment Description")
    submit = SubmitField("Create")

    def __init__(self, original_name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            investment = Investment.query.filter_by(name=name.data).first()
            if investment:
                raise ValidationError("This name is using.")
