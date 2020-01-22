import flask
import requests


app = flask.Flask(__name__)


@app.route('/_ah/<path:path>')
def app_engine(path):
    flask.abort(404, 'App Engine Methods not implemented')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if flask.request.scheme == 'http':
        flask.abort(400, 'Only HTTPS is supported.')

    old_host = flask.request.host
    new_host = '20200122t233313-dot-clybouw.appspot.com'

    method = flask.request.method
    url = flask.request.url.replace(old_host, new_host).replace('%2F', '/')
    headers = {k: v.replace(old_host, new_host)
               for k, v in flask.request.headers.items()
               if not (k in ['Forwarded']
                       or k.startswith('X-'))}
    headers['X-OAuth-Redirect'] = f'https://{old_host}'
    try:
        data = flask.request.get_data(as_text=True)
        data = data.replace(old_host, new_host)
    except UnicodeDecodeError:
        data = flask.request.get_data()

    resp = requests.request(method=method, url=url, headers=headers, data=data,
                            allow_redirects=False)

    new_headers = {k: v.replace(new_host, old_host)
                   for k, v in resp.headers.items()
                   if not (k in ['Content-Encoding', 'Transfer-Encoding']
                           or k.startswith('X-'))}
    try:
        new_content = resp.content.decode().replace(new_host, old_host)
    except UnicodeDecodeError:
        new_content = resp.content

    return new_content, resp.status_code, new_headers


if __name__ == '__main__':
    app.run()
