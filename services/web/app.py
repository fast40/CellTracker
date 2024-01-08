from flask import Flask, request, session, render_template, redirect, jsonify
import bcrypt
import time
from cell_tracker import experiments
from config import SITE_PASSWORD, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


def password_protected(func):
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        elif request.method == 'GET':
            return redirect(f'/authenticate?redirect={request.path}')
    
    wrapper.__name__ = func.__name__  # need this line to use the decorator more than once

    return wrapper


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        redirect_url = request.form['redirect_url']

        authenticated = bcrypt.checkpw(request.form['password'].encode(), SITE_PASSWORD)

        if authenticated:
            session['logged_in'] = True

            return redirect(redirect_url)
        else:
            time.sleep(1)

            return render_template('authenticate.html', redirect_url=redirect_url, failed=True)
    else:
        redirect_url = request.args.get('redirect') or '/'

        return render_template('authenticate.html', redirect_url=redirect_url)


@app.route('/logout')
def logout():
    session.pop('logged_in')

    return redirect('/')


@app.route('/')
@password_protected
def index():
    return render_template('index.html', experiments=experiments.get())


@app.route('/status')
@password_protected
def status():
    return jsonify(experiments.get())


@app.route('/upload', methods=['POST'])
@password_protected
def upload():
    experiments.process_files(request.files.getlist('files'))

    return redirect('/')


@app.route('/download', methods=['POST'])
@password_protected
def download():
    print(request.form.getlist('experiment'))
    return experiments.send_zipfile(request.form.getlist('experiment'))


@app.route('/delete', methods=['POST'])
@password_protected
def delete():
    experiments.delete(request.form.getlist('experiment'))

    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
