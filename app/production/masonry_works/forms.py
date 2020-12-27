from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    SubmitField,
)
from wtforms.validators import DataRequired, InputRequired, ValidationError
from app.models import Wall


class AddWallForm(FlaskForm):
    id = IntegerField("id")
    sector = StringField("sector", validators=[DataRequired()])
    level = StringField("level", validators=[DataRequired()])
    localization = StringField("localization")
    brick_type = StringField("brick_type", validators=[DataRequired()])
    wall_width = IntegerField("wall width", validators=[DataRequired()])
    wall_length = FloatField("wall length", validators=[DataRequired()])
    floor_ord = FloatField("floor ordinate", validators=[InputRequired()])
    ceiling_ord = FloatField("ceiling ordinate", validators=[InputRequired()])
    submit = SubmitField("submit")

    def validate_id(self, field):
        ids = [wall.id for wall in Wall.query.all()]
        if field.data in ids:
            raise ValidationError("Id must be unique!")


class EditWallForm(FlaskForm):
    sector = StringField("sector", validators=[DataRequired()])
    level = StringField("level", validators=[DataRequired()])
    localization = StringField("localization")
    brick_type = StringField("brick_type", validators=[DataRequired()])
    wall_width = IntegerField("wall width", validators=[DataRequired()])
    wall_length = FloatField("wall length", validators=[DataRequired()])
    floor_ord = FloatField("floor ordinate", validators=[InputRequired()])
    ceiling_ord = FloatField("ceiling ordinate", validators=[InputRequired()])
    submit = SubmitField("submit")


class HoleForm(FlaskForm):
    width = FloatField("width", validators=[InputRequired()])
    height = FloatField("height", validators=[InputRequired()])
    amount = IntegerField("amount", validators=[InputRequired()])
    submit = SubmitField("submit")


class ProcessingForm(FlaskForm):
    year = IntegerField("year", validators=[DataRequired()])
    month = StringField("month", validators=[DataRequired()])
    done = FloatField("done", validators=[InputRequired()])
    submit = SubmitField("submit")

    def validate_done(self, field):
        if field.data < 0:
            raise ValidationError("done values must be greater than 0!")
