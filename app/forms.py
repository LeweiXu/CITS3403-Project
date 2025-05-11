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

class ReopenActivityForm(FlaskForm):
    activity_id = HiddenField('Activity ID', validators=[DataRequired()])
    submit = SubmitField('Reopen Activity')

class DeleteActivityForm(FlaskForm):
    activity_id = HiddenField('Activity ID', validators=[DataRequired()])
    submit = SubmitField('Delete Activity')

class DeleteEntryForm(FlaskForm):
    entry_id = HiddenField('Entry ID', validators=[DataRequired()])
    submit = SubmitField('Delete Entry')

class ViewSharedDataForm(FlaskForm):
    target_user = StringField('Target User', validators=[DataRequired(), Length(min=3, max=50)])
    data_type = SelectField('Data Type', choices=[
        ('analysis', 'Analysis'),
        ('activities', 'Activities'),
        ('history', 'History')
    ], validators=[DataRequired()])

class DeleteSharedUserForm(FlaskForm):
    target_user = StringField('Target User', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Delete Shared User')

class ShareWithUserForm(FlaskForm):
    target_user = StringField('Target User', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Share with User')