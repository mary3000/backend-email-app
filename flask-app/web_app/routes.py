from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from itsdangerous import SignatureExpired, BadSignature
from werkzeug.urls import url_parse

from web_app import app, db, channel, queue_name, serializer
from web_app.forms import LoginForm, RegistrationForm, MailResendForm
from web_app.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }]
    return render_template('index.html', user=user, title='Home', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if not user.confirmed:
            flash('Unconfirmed account. Check your email first!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def send_confirmation(email, token):
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=email + ' ' + token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():

        token = serializer.dumps(form.email.data)

        user = User(username=form.username.data, email=form.email.data, confirmed=False, token=token)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        send_confirmation(form.email.data, token)

        flash('Confirmation message send. Check your email and follow the link.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    form = MailResendForm()
    if form.validate_on_submit():
        token = serializer.dumps(form.email.data)
        user = User.query.filter_by(email=form.email.data).first()
        user.token = token
        db.session.commit()
        send_confirmation(form.email.data, token)
        return render_template('confirm.html',
                               text='Confirmation message send. Check your email and follow the link.',
                               form=form,
                               failed=True)

    cur_token = request.args.get('token', '')
    if cur_token == '':
        return render_template('confirm.html', text='Resend confirmation message', form=form, failed=True)

    user = User.query.filter_by(token=cur_token).first()

    try:
        cur_mail = serializer.loads(user.token, 60 * 60 * 2)
        if cur_mail != user.email:
            raise NameError
        user.confirmed = True
        db.session.commit()
    except NameError:
        return render_template('confirm.html', text='Wrong mail', form=form, failed=True)
    except SignatureExpired:
        return render_template('confirm.html', text='Expired', form=form, failed=True)
    except BadSignature:
        return render_template('confirm.html', text='Bad signature', form=form, failed=True)
    except:
        return render_template('confirm.html', text='Something went wrong', form=form, failed=True)

    return render_template('confirm.html', text='Confirmed! You may now login', failed=False)

