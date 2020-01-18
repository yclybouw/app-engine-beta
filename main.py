import authlib.integrations.flask_client
import flask


app = flask.Flask(__name__)
app.config.from_object('settings')

oauth = authlib.integrations.flask_client.OAuth(app)
oauth.register('google', fetch_token=lambda: flask.session.get('google_token'))


# Security warning: in production use a server side cache, like REDIS, instead!
def store_and_return_token(name, token):
    flask.session[name] = token
    return token


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/google')
def hello_google():
    if 'google_token' not in flask.session:
        return flask.redirect(flask.url_for('login_google'))
    profile = oauth.google.get('oauth2/v1/userinfo?alt=json').json()
    profile_html = ('Hello {name}, this is your profile picture: <br />'
                    '<img src="{picture}">'.format(**profile))
    return profile_html


@app.route('/google/login')
def login_google():
    redirect_uri = flask.url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/authorize')
def authorize_google():
    token = oauth.google.authorize_access_token()
    flask.session['google_token'] = token
    return flask.redirect(flask.url_for('hello_google'))


if __name__ == '__main__':
    app.run()
