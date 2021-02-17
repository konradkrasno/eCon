import datetime

from flask import g
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import Worker


class TaskForm(FlaskForm):
    description = StringField("Task description", validators=[DataRequired()])
    deadline = DateField("Deadline, format: Y-M-D")
    priority = SelectField("Priority", choices=[i for i in range(1, 6)])
    executor_name = StringField("Executor name", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_deadline(self, deadline):
        if deadline.data:
            if deadline.data < datetime.date.today() + datetime.timedelta(days=1):
                raise ValidationError("Deadline must be tomorrow at the earliest.")

    def validate_executor_name(self, executor_name):
        if not Worker.get_by_username(g.current_invest.id, executor_name.data).id:
            raise ValidationError(
                "We can not find worker with this name. Check typing and try again."
            )


class ProgressForm(FlaskForm):
    progress = IntegerField("Progress")
    submit = SubmitField("Submit")

    def validate_progress(self, progress):
        if not isinstance(progress.data, int):
            progress.data = 0
        if progress.data < 0:
            raise ValidationError("Progress value can not be negative!")
        if progress.data > 100:
            raise ValidationError("Progress value can not be greater than 100!")
