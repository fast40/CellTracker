from flask import Flask, request, session, render_template, redirect
from site_config import *
import bcrypt
import time

app = Flask(__name__)
app.config.from_pyfile('flask_config.py')


def password_protected(func):
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            return authenticate(request.path)
    
    return wrapper


@app.route('/')
@password_protected
def cell_tracker():
    return render_template('cell_tracker.html')


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate(redirect_url='/'):
    if request.method == 'POST':
        authenticated = bcrypt.checkpw(request.form['password'].encode(), SITE_PASSWORD)

        if authenticated:
            session['logged_in'] = True

            return redirect(request.form['redirect_url'])
        else:
            time.sleep(1)

            return render_template('authenticate.html', redirect_url=request.form['redirect_url'], failed=True)
    else:
        return render_template('authenticate.html', redirect_url=redirect_url)


@app.route('/logout')
def logout():
    session.pop('logged_in')

    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
