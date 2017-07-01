from flask import Flask, render_template, url_for, redirect, session, logging, request, flash
from forms import RegisterForm, LoginForm, WishlistAddForm, ResetPasswordForm, ChangeNameForm, ForgotPasswordForm, ChangePasswordForm
from passlib.hash import sha256_crypt
# from flask_mysqldb import MySQL
from functools import wraps
import pymysql as pm
from database_work import get_all_wishlists, add_wishlist
from mobile import get_wishlist_id
from mail_sender import send_single_mail
from security import secure
from details import APP_SECRET_KEY, SALT1, SALT2
from details import User, Wishlist, Item, verified
from flask_sqlalchemy import SQLAlchemy
import time
import os

def login_required(f):
	@wraps(f)
	def func(*args, **kwargs):
		if session.get('logged_in', None):
			return f(*args, **kwargs)
		else:
			flash('Log in to see the content', 'danger')
			return redirect(url_for('login'))
	return func


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
db = SQLAlchemy(app)

app.secret_key = APP_SECRET_KEY


@app.route('/')
def index():
	session['logged_in'] = session.get('logged_in', False)
	if session['logged_in']:
		return redirect(url_for('home'))
	return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == "POST":
		if form.validate():
			
			name = form.name.data
			email = form.email.data
			password = sha256_crypt.encrypt(str(form.password.data))
			
			try:
				res = db.session.query(verified).filter_by(email=email).first()
				print(res)
				if res:
					if res.confirmed:
						flash('Account for this email has already been activated, Log in to use', 'danger')
					else:
						flash('This email has already been registered, check your mail to verify', 'info')

					return redirect(url_for('login'))

				else:
					new_user = User(name=name, email=email, password=password)
					ver = verified(email=email, confirmed=False)
					
					
					db.session.add(ver)
					db.session.add(new_user)
					
					db.session.commit()
					db.session.close()

			except Exception as e:
				error = 'An error occurred, registration failed! Try again later!'
				print(e)
				return render_template('error.html', error=error)

			
			ts = secure(app)
			token = ts.dumps(email, salt=SALT1)
			# print(token)
			subject = "Confirm your email"

			confirm_url = url_for('confirm_email', token=token, _external=True)
			body = render_template('email/activation.html', confirm_url=confirm_url)

			send_single_mail(email, subject, body)
			flash("Registration successful, a verification mail has been sent to your email address", 'success')
			return redirect(url_for('index'))

		else:
			flash('Correct the following errors', 'danger')
			return render_template('register.html', form=form)
	
	else:
		return render_template('register.html', form=form)




@app.route('/confirm/<token>')
def confirm_email(token):

	email = None
	name = None
	# db = None
	cur = None
	ts = secure(app)
	try:
		
		try:
			email = ts.loads(token, salt=SALT1, max_age=86400)
			
		except:
			db.session.query(verified).filter_by(email=email).delete()
			db.session.query(User).filter_by(email=email).delete()
			db.session.commit()
			db.session.close()
			error = "An error occurred, registration failed! Try again later"
			return render_template('error.html', error=error)

		res = db.session.query(verified).filter_by(email=email).first()
		# res = cur.execute("select * from users where email = %s", (email,))
		if res:
			res.confirmed = True
			db.session.commit()
			db.session.close()
			# cur.execute('update `verified` set `confirmed` = %s where `email` = %s', (True, email))
			# db.commit()
			
			flash('Email confirmed. You can now log in!', 'success')
			return redirect(url_for('login'))
		else:
			
			flash('Invalid email or email not registered', 'danger')
			return redirect(url_for('index'))
	except:
		error = 'An error occurred, registration failed! Try again later!'
				
		return render_template('error.html', error=error)




@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if request.method == "POST":
		if form.validate():
			
			email = form.email.data
			password_entered = form.password_entered.data
			
			try:
				res = db.session.query(verified).filter_by(email=email).first()
				# res = cur.execute("select * from `verified` where email = %s", (email,))
				if res:
					if not res.confirmed:
					# if not cur.fetchone()['confirmed']:
						
						flash('This email is not confirmed', 'danger')
						return render_template('login.html', form=form)

				else:
					
					flash('Invalid username/password', 'danger')
					return render_template('login.html', form=form)

				result = db.session.query(User).filter_by(email=email).first()
				# result = cur.execute("Select * from users where email = %s", (email,))
				
				if result:

					# data = cur.fetchone()
					# pwd = data['password']
					# name = data['name']
					pwd = result.password
					name = result.name
					db.session.close()
					
					if sha256_crypt.verify(password_entered, pwd):
						
						app.logger.info('Passwords match')
						session['logged_in'] = True
						session['username'] = name
						session['email'] = email
						return redirect(url_for('home'))
					
					else:
						app.logger.info("Passwords didn't match")

				flash('Invalid username/password', 'danger')
				return render_template('login.html', form=form)
			
			except Exception as e:
				print(e)

				error = 'An error occurred, login failed! Try again later!'
				return render_template('error.html', error=error)

		
		else:
			
			flash("Invalid username/password", "danger")
			return render_template('login.html', form=form)
		
	else:
		return render_template('login.html', form=form)




@app.route('/home', methods=["POST", "GET"])
@login_required
def home():
	try:	
		# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:
		# 	email = session['email']
		# 	query = 'select * from `wishlists` where `email` = %s'
		# 	res = cur.execute(query, (email,))
		# 	wishlists = cur.fetchall()
		email = session['email']
		wishlists = db.session.query(Wishlist).filter_by(email=email).all()
		if not wishlists:
			flash("you are not tracking any wishlist", 'info')
		
		db.session.close()
		return render_template('home.html', wishlists=wishlists)
	except Exception as e:
		print(e)
		error = 'An error occurred while loading your wishlists. Try again later!'
		return render_template('error.html', error=error)
		


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
	form = WishlistAddForm(request.form)
	if request.method == "POST":
		if form.validate():
			wl_url = form.wl_url.data.strip()
			wl_id = get_wishlist_id(wl_url)
			if wl_id:
				name = form.name.data
				name = name if name else "Amazon Wishlist"
				res = add_wishlist(session['email'], wl_id, name)
				if res == -1:
					flash('You are already tracking this wishlist', 'info')
				elif res == -2:
					flash('Error adding wishlist, try again later!', 'danger')
				else:
					flash('Wishlist added', 'success')
				return redirect(url_for('home'))
			else:
				flash('Invalid url try again', 'danger')
				return redirect(url_for('home'))
		else:
			return render_template('wishlist_add.html', form=form)
	else:
		return render_template('wishlist_add.html', form=form)




@app.route('/delete/<wl_id>')
@login_required
def delete(wl_id):
	try:
		# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:
		email = session['email']
		# query = 'delete from `wishlists` where `email` = %s and `wishlist_id` = %s'
		# res = cur.execute(query, (email, wl_id))
		# db.commit()
		res = db.session.query(Wishlist).filter_by(email=email,wishlist_id=wl_id).delete()
		db.session.commit()
		db.session.close()
	
		if res:
			flash('Deleted successfully', 'success')
		else:
			flash('Wishlist couldn\'t be deleted', 'danger')

		
		return redirect(url_for('home'))

	except:
		error = 'An error occurred while deleting your wishlist. Try again later!'
		return render_template('error.html', error=error)





@app.route('/refresh')
@login_required
def refresh():
	get_all_wishlists(session['email'])
	flash('Updated','info')
	return redirect(url_for('home'))




@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
	form = ChangeNameForm(request.form)
	if request.method == "POST":
		if form.validate():
			# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:
			name = form.new_name.data
			password = form.password.data
			email = session['email']
			# result = cur.execute("Select * from users where email = %s", (email,))
			result = db.session.query(User).filter_by(email=email).first()
			
			if result:

				# data = cur.fetchone()
				pwd = result.password
				
				if not sha256_crypt.verify(password, pwd):
					app.logger.info('Passwords don\'t match')
					flash('Wrong password, try again','danger')
					return render_template('profile.html', form=form)
				else:
					# query = "update users set name = %s where email = %s"
					# cur.execute(query, (name, email))
					# db.commit()
					result.name = name
					db.session.commit()
					db.session.close()
					session['username'] = name
					flash('Successfully updated!', 'success')
					return redirect(url_for('home'))

			else:
				error = "an error occurred!"
				return render_template('error.html', error=error)

		else:
			flash('Correct the following errors', 'danger')
			return render_template('profile.html',form=form)

	else:
		return render_template('profile.html', form=form)



@app.route('/update', methods=["GET" ,"POST"])
@login_required
def update():
	form = ChangePasswordForm(request.form)
	if request.method == "POST":
		if form.validate():

			old_pass = form.old_pass.data
			new_pass = form.new_pass.data
			email = session['email']
			try:
				# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:
			
				# result = cur.execute("Select * from users where email = %s", (email,))
				result = db.session.query(User).filter_by(email=email).first()
				
				if result:

					# data = cur.fetchone()
					# pwd = data['password']
					pwd = result.password
					
					if not sha256_crypt.verify(old_pass, pwd):
						
						app.logger.info('Passwords don\'t match')
						flash('Wrong password, try again','danger')
						return render_template('email/update_password.html', form=form)
					else:
						# query = "update users set password = %s where email = %s"
						# cur.execute(query, (sha256_crypt.encrypt(str(new_pass)), email))
						result.password = sha256_crypt.encrypt(new_pass)
						db.session.commit()
						db.session.close()
						# db.commit()
						
						flash('Successfully updated!', 'success')
						return redirect(url_for('home'))
				
				session.clear()
				error = "An error occurred!"
				return render_template('error.html', error=error)
			except:
				error = 'An error occurred. Try again later!'
				return render_template('error.html', error=error)
		else:
			flash('Correct the following errors!', 'success')
			return render_template('email/update_password.html', form=form)
	else:
		return render_template('email/update_password.html', form=form)




@app.route('/reset', methods=["GET", "POST"])
def reset():
	form = ForgotPasswordForm(request.form)
	if request.method == "POST":
		if form.validate():
			email = form.email.data
			try:
				# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:
				# res = cur.execute('select * from verified where email = %s and confirmed = %s', (email, True))

				res = db.session.query(verified).filter_by(email=email, confirmed=True).first()
				db.session.close()
				
				if res:
					ts = secure(app)
					token = ts.dumps(email, salt=SALT2)
					subject = "Reset your password"

					reset_url = url_for('recover', token=token, _external=True)
					body = render_template('email/password_recovery.html', reset_url=reset_url)

					send_single_mail(email, subject, body)

				session.clear()
				flash("You'll receive a recovery mail if the email is registered", 'info')
				return redirect(url_for('login'))
			except Exception as e:
				print(e)
				error = 'An error occurred. Try again later!'
				return render_template('error.html', error=error)
		else:
			flash('Correct the following errors', 'danger')
			return render_template('email/forgot_password.html', form=form)
	else:
		return render_template('email/forgot_password.html', form=form)




@app.route('/recover/<token>', methods=["GET", "POST"])
def recover(token):
	form = ResetPasswordForm(request.form)
	if request.method == "POST":
		if form.validate():
			ts = secure(app)
			email = None
			try:
				email = ts.loads(token, salt=SALT2, max_age=86400)
			except Exception as e:
				print(e)
				error = 'An error occurred!'
				return render_template('error.html', error=error)
			try:
				# with pm.connect(DATABASE_URI, DB_USER, DB_PASSWORD, DB_DATABASE, cursorclass=pm.cursors.DictCursor) as cur:

				# res = cur.execute('select * from verified where email = %s and confirmed = %s', (email, True))
				res = db.session.query(verified).filter_by(email=email, confirmed=True).first()
				if res:
					res1 = db.session.query(User).filter_by(email=email).first()
					new_pass = sha256_crypt.encrypt(form.new_pass.data)
					# cur.execute('update users set password = %s where email = %s', (new_pass, email))
					# db.commit()
					res1.password = new_pass
					db.session.commit()
					db.session.close()
					
					flash('Password reset successful', 'success')
					return redirect(url_for('login'))
				else:
					
					error = "An error occurred"
					return render_template('error.html', error=error)
			except Exception as e:
				print(e)
				error = 'An error occurred. Try again later!'
				return render_template('error.html', error=error)
		
		else:
			flash('Correct the following errors', 'danger')
			return render_template('email/password_reset.html', form=form)
			
	
	else:
		ts = secure(app)
		email = None
		try:
			email = ts.loads(token, salt=SALT2, max_age=86400)
		except:
			error = 'An error occurred!'
			return render_template('error.html', error=error)
		
		return render_template('email/password_reset.html', form=form)





@app.route('/about')
def about():
	return render_template('about.html')




@app.route('/logout')
def logout():
	session.clear()
	flash('You were successfully logged out', 'success')
	return redirect(url_for('index'))





if __name__ == '__main__':

	app.run(debug=True, port=8000)



