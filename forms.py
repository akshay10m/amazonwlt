from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField, Form
from wtforms.validators import Email, DataRequired, Length, EqualTo, URL


class RegisterForm(Form):
	
	name = StringField('Name', 
		validators = [Length(min=1, max=30), DataRequired('Field required')]
		)

	email = TextField('Email', 
		validators = [Email(), DataRequired('Field required')]
		)

	password = PasswordField('Password',
		validators = [EqualTo('confirm', message="Passwords must match"), Length(min=6,max=14),
		DataRequired('Field required')]
		)

	confirm = PasswordField('Repeat password')


class LoginForm(Form):
	 
	 email = TextField('Email', 
	 		validators = [Email(), DataRequired('Field required')]
	 	)

	 password_entered = PasswordField('Password',[
			Length(min=6,max=14), DataRequired('Field required')]
		)


class ForgotPasswordForm(Form):
	email = TextField('Enter your registered email id', 
			validators = [DataRequired('Enter email'), Email()]
	)


class WishlistAddForm(Form):

	wl_url = TextField('Enter the wishlist url',
		validators = [URL(), DataRequired()]
	)
	name = TextField('Enter a name for your wishlist', default="Amazon Wishlist")


class ChangeNameForm(Form):
	new_name = StringField('Name', 
		validators = [Length(min=1, max=30), DataRequired('Field required')]
		)
	password = PasswordField('password',
        validators = [DataRequired(), Length(min=6, max=14)]
    )


class ChangePasswordForm(Form):
	
    old_pass = PasswordField('Current password',
        validators = [DataRequired(), Length(min=6, max=14)]
    )
    new_pass = PasswordField('New password',
        validators = [DataRequired(), Length(min=6, max=14)]
    )


class ResetPasswordForm(Form):
	new_pass = PasswordField('Enter your new password',
			validators = [DataRequired(), Length(min=6, max=14), EqualTo('confirm', message='Passwords must match')]
		)
	confirm = PasswordField('Confirm Password',
			validators = [DataRequired()]
		)
