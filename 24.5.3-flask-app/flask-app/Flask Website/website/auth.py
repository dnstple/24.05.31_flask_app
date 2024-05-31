from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user



auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash(f'Hello {user.first_name}!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password', category='error')
        else:
            flash('User does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email is already asscociated with an account', category='error')

        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
            
        elif len(firstname) < 2:
            flash('Name must be greater than 2 characters', category='error')
            
        elif password1 != password2:
            flash('Passwords must match', category='error')

        elif len(password1) < 3:
            flash('Password must be greater than 3 characters', category='error')

        else:
            new_user = User(email=email, first_name=firstname, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash(f'Account created. Hello, {firstname}!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

        #create user 

    return render_template( "sign-up.html", user=current_user)



