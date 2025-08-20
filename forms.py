from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, URL, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    website = StringField('Website', validators=[Optional(), URL()])
    github_username = StringField('GitHub Username', validators=[Optional(), Length(max=100)])
    linkedin_profile = StringField('LinkedIn Profile', validators=[Optional(), URL()])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    content = TextAreaField('Detailed Content', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('desktop', 'Desktop Application'),
        ('ai', 'AI/Machine Learning'),
        ('data', 'Data Science'),
        ('game', 'Game Development'),
        ('other', 'Other')
    ])
    tags = StringField('Tags (comma-separated)', validators=[Optional(), Length(max=500)])
    github_link = StringField('GitHub Repository', validators=[Optional(), URL()])
    demo_link = StringField('Demo Link', validators=[Optional(), URL()])
    image = FileField('Project Image', validators=[FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    video = FileField('Project Video', validators=[FileAllowed(['mp4', 'avi', 'mov'], 'Videos only!')])
    is_published = BooleanField('Publish immediately')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=1000)])
