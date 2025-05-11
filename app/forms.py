from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, IntegerField
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

class AddActivityForm(FlaskForm):
    activity_name = StringField('Activity Name', validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Add Activity')

class AddEntryForm(FlaskForm):
    activity_id = HiddenField('Activity ID', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Entry')