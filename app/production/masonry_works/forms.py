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
    id = IntegerField("Id")
    sector = StringField("Sector", validators=[DataRequired()])
    level = StringField("Level", validators=[DataRequired()])
    localization = StringField("Localization")
    brick_type = StringField("Brick Type", validators=[DataRequired()])
    wall_width = IntegerField("Wall Width", validators=[DataRequired()])
    wall_length = FloatField("Wall Length", validators=[DataRequired()])
    floor_ord = FloatField("Floor Ordinate", validators=[InputRequired()])
    ceiling_ord = FloatField("Ceiling Ordinate", validators=[InputRequired()])
    submit = SubmitField("Submit")

    def validate_id(self, field):
        ids = [wall.id for wall in Wall.query.all()]
        if field.data in ids:
            raise ValidationError("Id must be unique!")


class EditWallForm(FlaskForm):
    sector = StringField("Sector", validators=[DataRequired()])
    level = StringField("Level", validators=[DataRequired()])
    localization = StringField("Localization")
    brick_type = StringField("Brick Type", validators=[DataRequired()])
    wall_width = IntegerField("Wall Width", validators=[DataRequired()])
    wall_length = FloatField("Wall Length", validators=[DataRequired()])
    floor_ord = FloatField("Floor Ordinate", validators=[InputRequired()])
    ceiling_ord = FloatField("Ceiling Ordinate", validators=[InputRequired()])
    submit = SubmitField("Submit")


class HoleForm(FlaskForm):
    width = FloatField("Width", validators=[InputRequired()])
    height = FloatField("Height", validators=[InputRequired()])
    amount = IntegerField("Amount", validators=[InputRequired()])
    submit = SubmitField("Submit")


class ProcessingForm(FlaskForm):
    year = IntegerField("Year", validators=[DataRequired()])
    month = StringField("Month", validators=[DataRequired()])
    done = FloatField("Done", validators=[InputRequired()])
    submit = SubmitField("Submit")

    def validate_done(self, field):
        if field.data < 0:
            raise ValidationError("Done value must be greater than 0!")
