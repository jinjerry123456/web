from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional, URL
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import CheckboxInput
from wtforms import widgets
from . import db
from datetime import datetime
from .models import Tag


# the form for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# the form for registration


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(message="Username is required."), Length(min=2, max=20)])
    email = StringField('Email', validators=[
                        DataRequired(message="Email is required"), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Regexp(r'^(?=.*[A-Z])(?=.*\d).{6,}$',
               message="Password must have at least one uppercase letter and one digit.")])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    # choose a role teacher/student
    role = SelectField('Role', choices=[
                       ('student', 'Student'), ('teacher', 'Teacher')], default='student')
    submit = SubmitField('Register')


# the form for course edit
class CourseForm(FlaskForm):
    title = StringField('Tittle', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(),
                                                           Length(
        max=200,
        message="Description must less then 200 words.")])
    video_url = URLField('Video URL', validators=[Optional(), URL()])
    image_url = URLField('Image URL', validators=[Optional(), URL()])
    tag = QuerySelectMultipleField('Tags',
                                   query_factory=lambda: Tag.query.all(),
                                   get_label='name',
                                   widget=widgets.ListWidget(
                                       prefix_label=False),
                                   option_widget=widgets.CheckboxInput(),
                                   allow_blank=True)
    submit = SubmitField('Update Course')

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)


# manager form
class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
                       ('student', 'Student'), ('teacher', 'Teacher'), ('manager', 'Manager')])
    submit = SubmitField('Update')


# create the course
class CreateCourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(
        max=200,
        message="Description must less then 200 words.")])
    video_url = StringField('Video URL', validators=[Optional(), URL()])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    tag = QuerySelectMultipleField('Tags',
                                   query_factory=lambda: Tag.query.all(),
                                   get_label='name',
                                   widget=widgets.ListWidget(
                                       prefix_label=False),
                                   option_widget=widgets.CheckboxInput(),
                                   allow_blank=True)
    submit = SubmitField('Create Course')

    def __init__(self, *args, **kwargs):
        super(CreateCourseForm, self).__init__(*args, **kwargs)

# comment of the course


class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')


# change password

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Regexp(r'^(?=.*[A-Z])(?=.*\d).{6,}$',
               message="Password must have at least one uppercase letter and one digit.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Change Password')
