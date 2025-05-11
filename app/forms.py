from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class AddEntryForm(FlaskForm):
    activity_id = HiddenField('Activity ID', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Add Entry')

class EndActivityForm(FlaskForm):
    activity_id = HiddenField('Activity ID', validators=[DataRequired()])
    rating = IntegerField('Rating (1.0-10.0)', validators=[Optional(), NumberRange(min=1, max=10)])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Submit')

class ShareDataForm(FlaskForm):
    target_user = StringField('Target User', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Search and Share')

from wtforms import SelectField, StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional

class AddActivityForm(FlaskForm):
    media_type = SelectField('Media Type', choices=[
        ('', 'Select Media Type'),
        ('Visual Media', 'Visual Media'),
        ('Audio Media', 'Audio Media'),
        ('Text Media', 'Text Media'),
        ('Interactive Media', 'Interactive Media')
    ], validators=[DataRequired()])

    # Disable choice validation by setting validate_choice=False
    media_subtype = SelectField('Media Subtype', validate_choice=False, validators=[Optional()])

    media_name = StringField('Media Name', validators=[DataRequired()])
    submit = SubmitField('Add Activity')
