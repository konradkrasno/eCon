from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    PasswordField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, InputRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WallForm(FlaskForm):
    object = StringField("object", validators=[DataRequired()])
    level = StringField("level", validators=[DataRequired()])
    localization = StringField("localization")
    brick_type = StringField("brick_type", validators=[DataRequired()])
    wall_width = IntegerField("wall width", validators=[DataRequired()])
    wall_length = FloatField("wall length", validators=[DataRequired()])
    floor_ord = FloatField("floor ordinate", validators=[InputRequired()])
    ceiling_ord = FloatField("ceiling ordinate", validators=[InputRequired()])
    submit = SubmitField("submit")


class HoleForm(FlaskForm):
    hole_width = FloatField("hole width", validators=[InputRequired()])
    hole_height = FloatField("hole height", validators=[InputRequired()])
    holes_amount = IntegerField("holes amount", validators=[InputRequired()])
    submit = SubmitField("submit")


class ProcessingForm(FlaskForm):
    year = IntegerField("year", validators=[DataRequired()])
    month = StringField("month", validators=[DataRequired()])
    done = FloatField("done", validators=[InputRequired()])
    submit = SubmitField("submit")
