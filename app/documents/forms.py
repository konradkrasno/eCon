import os

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class NewFolderForm(FlaskForm):
    folder_name = StringField("Folder Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self, folder_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_path = folder_path

    def validate_folder_name(self, folder_name):
        if os.path.exists(os.path.join(self.folder_path, folder_name.data)):
            raise ValidationError("Folder with this name already exists!")
