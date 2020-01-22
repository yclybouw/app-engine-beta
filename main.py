import authlib.integrations.flask_client
import flask

try:
    import googleclouddebugger
    googleclouddebugger.enable()
except ImportError:
    pass


app = flask.Flask(__name__)
app.config.from_object('settings')


class TokenStore:
    """
    Manage token in the Flask Session. For security reasons, however, in
    production store it in a real database.
    """
    def __init__(self, name):
        self.name = name

    def store(self, token):
        flask.session[f'{self.name}_token'] = token

    def fetch(self):
        return flask.session.get(f'{self.name}_token')

    def update(self, token, refresh_token=None, access_token=None):
        flask.session[f'{self.name}_token'] = token


oauth = authlib.integrations.flask_client.OAuth(app)
google_token = TokenStore('google')
oauth.register(
    name='google',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/',
    client_kwargs={'scope': 'profile'},
    fetch_token=google_token.fetch,
    update_token=google_token.update,
)


@app.route('/')
def index():
    index_html = (f'Hello, <a href="{flask.url_for("show_google_profile")}">'
                  f'click here to see your Google Profile</a>.')
    return index_html


@app.route('/google')
def show_google_profile():
    if not google_token.fetch():
        return flask.redirect(flask.url_for('login_google'))
    profile = oauth.google.get('oauth2/v1/userinfo?alt=json').json()
    profile_html = ('Hello {name}, this is your profile picture: <br />'
                    '<img src="{picture}">'.format(**profile))
    return profile_html


@app.route('/google/login')
def login_google():
    # Detect our transparent reverse proxy through a specific header named
    # X-OAuth-Redirect. This is needed because authorize_access_token
    # is a server-to-server call using redirect_uri, but bypassing the proxy.
    redirect_proxy = flask.request.headers.get('X-OAuth-Redirect')
    if redirect_proxy:
        redirect_uri = redirect_proxy + flask.url_for('authorize_google')
    else:
        redirect_uri = flask.url_for('authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/authorize')
def authorize_google():
    token = oauth.google.authorize_access_token()
    google_token.store(token)
    return flask.redirect(flask.url_for('show_google_profile'))


if __name__ == '__main__':
    app.run()
