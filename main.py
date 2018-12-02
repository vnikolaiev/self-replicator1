import random
import string
import os
from flask import Flask, request, redirect, render_template, session, url_for
from GitHub import GitHub, GitHubResultCode

app = Flask(__name__)
app.config.from_pyfile('config')


def get_token():
    return session.get('token', None)


def set_token(token):
    session['token'] = token


def listdir_nohidden(path):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
        files[:] = [f for f in files if not f.startswith('.') and not f.startswith('__') and f != 'source-context.json']
        for file in files:
            yield os.path.join(root, file)[2:]


"""
Replace secrets in config
param: s: string or bytes, (required), string with config file content
param: keys: tuple of strings, (required), keys to replace values with <REPLACE_ME>
"""
def secret_replacer(s, keys):
    if type(s) is bytes:
        sin = s.decode()
    else:
        sin = s
    sout = ''
    for a in sin.split('\n'):
        b = a.split('=')
        if b[0].rstrip().startswith(keys):
            b[1] = " '<REPLACE_ME>'"
        sout += '='.join(b) + '\n'
    if type(s) is bytes:
        return sout.encode()
    else:
        return sout


github = GitHub(get_token)


@app.route('/', methods=['GET'])
def index():
    session['rand'] = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    error = request.args.get('error', default='')
    success = request.args.get('success', default='')
    if error:
        return render_template(app.config['INDEX_TEMPLATE'], error=error)
    elif success:
        return render_template(app.config['INDEX_TEMPLATE'], success=success)
    else:
        return render_template(app.config['INDEX_TEMPLATE'])


@app.route('/callback', methods=['POST', 'GET'])
def callback():
    if request.method == 'POST':
        if request.form.get('state', None) == session['rand']:
            code = request.form.get('code', None)
        else:
            return redirect(url_for('index', error='state param doesn\'t match. Request has been created by 3rd party'))
    else:
        if request.args.get('state', None) == session['rand']:
            code = request.args.get('code', None)
        else:
            return redirect(url_for('index', error='state param doesn\'t match. Request has been created by 3rd party'))

    if code is not None:
        token = github.get_token_from_github(app.config['GITHUB_CLIENT_ID'], app.config['GITHUB_CLIENT_SECRET'], code)
        if token is not None:
            set_token(token)
        else:
            return redirect(url_for('index', error='GitHub account token retrieve failed'))
        return redirect(url_for('index', success='Successfully authenticated'))
    else:
        return redirect(url_for('index', error='code param hasn\'t passed'))


@app.route('/clone', methods=['GET'])
def clone():
    repo_name = request.args.get('reponame', None)
    if repo_name is not None and repo_name != '':
        rr = github.create_repo(repo_name)
        # code 201 - repo created
        if rr.code == 201:
            files = listdir_nohidden('.')
            for f in files:
                with open(f, 'rb') as fd:
                    content = fd.read()
                    if f == 'config':
                        content = secret_replacer(content, keys=('GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET'))
                    rf = github.put_file(repo_name, f, content)
                    if rf.code == 401:
                        set_token(None)
                        return redirect(url_for('index', error="Error: " + rf.message))
                    elif rf.code != 201:
                        return redirect(url_for('index', error="Error: " + rf.message))
            return redirect(url_for('index', success="Repository {repo_name} created".format(repo_name=repo_name)))
        elif rr.code == 401:
            set_token(None)
            return redirect(url_for('index', error="Error: " + rr.message))
        else:
            return redirect(url_for('index', error="Error: " + rr.message))
    else:
        return redirect(url_for('index', error="Invalid repository name"))


if __name__ == '__main__':
    app.run(debug=True)
