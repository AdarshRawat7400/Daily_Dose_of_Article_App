from wtforms import Form, TextAreaField, StringField, PasswordField, validators,SubmitField
from flask_wtf import FlaskForm
from articleapp.models import Users,Articles
from flask_wtf.file import FileField, FileAllowed
import re
from flask import session
from slugify import slugify 


class RegisterForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField("Username",[validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField('Email',[validators.Length(min=6, max=50),validators.DataRequired()])
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='Password Do Not Match')
    ])
    confirm = PasswordField('Confirm Password',[validators.DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise validators.ValidationError('Username is already taken')

    def validate_email(self,email):
        if not re.match(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email.data):
            raise validators.ValidationError('Invalid Email')
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise validators.ValidationError('Email is already taken')


class UpdateProfileForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField("Username",[validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField('Email',[validators.Length(min=6, max=50),validators.DataRequired()])
    profile_img = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Profile')
    

    def validate_username(self,username):
        user = Users.query.filter_by(id=session['id']).first()

        if username.data != user.username:
            temp = Users.query.filter_by(username=username.data).first()
            if temp:
                raise validators.ValidationError('Username is already taken')
        

    def validate_email(self,email):
        user = Users.query.filter_by(id=session['id']).first()
        if not re.match(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email.data):
            raise validators.ValidationError('Invalid Email')
        elif email.data != user.email:
            print("IM HERE")
            temp = Users.query.filter_by(email=email.data).first()
            if temp:
                print(temp.email)
                raise validators.ValidationError('Username is already taken')





class LoginForm(FlaskForm):
    username = StringField('Username',[validators.Length(min=4, max=25)])
    password = PasswordField('Password',[
        validators.DataRequired(),
    ])
    submit = SubmitField('Login')



class ArticleForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField("Body",[validators.Length(min=30)])

    def validate_title(self,title):
        user = Articles.query.filter_by(author=session['username']).first()
    
        article = Articles.query.filter_by(slug=slugify(title.data)).first()
        if article:
            raise validators.ValidationError('Article title is already taken')

class UpdateArticleForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField("Body",[validators.Length(min=30)])



    

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email',[validators.Length(min=6, max=50),validators.DataRequired()])
    submit = SubmitField('Request Password Reset')
    def validate_email(self,email):
        if not re.match(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}", email.data):
            raise validators.ValidationError('Invalid Email')

        if not Users.query.filter_by(email=email.data).first():
            raise validators.ValidationError('Email not registered')
    

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm_password',message='Password Do Not Match')
    ])
    confirm_password = PasswordField('Confirm Password',[validators.DataRequired()])
    submit = SubmitField('Reset Password')
