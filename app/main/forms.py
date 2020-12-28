from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
)


class WarrantyForm(FlaskForm):
    yes = SubmitField("Yes")
    no = SubmitField("No")
