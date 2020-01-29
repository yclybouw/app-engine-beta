import os

import flask
import requests

import googleapiclient.discovery


def get_latest_version_host():
    """
    Return the hostname of the latest version of the default service.
    Example: 20200129t130254-dot-myproject.appspot.com
    """
    apps_id = os.environ['GOOGLE_CLOUD_PROJECT']
    service = googleapiclient.discovery.build('appengine', 'v1')
    versions_api = service.apps().services().versions()
    versions = versions_api.list(appsId=apps_id, servicesId='default').execute()
    running_versions = [version for version in versions['versions']
                        if version['servingStatus'] == 'SERVING']
    version = max(running_versions, key=lambda v: v['createTime'])
    return f"{version['id']}-dot-{apps_id}.appspot.com"


app = flask.Flask(__name__)
new_host = get_latest_version_host()


@app.route('/_ah/<path:path>')
def app_engine(path):
    flask.abort(404, 'App Engine Methods not implemented')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Repeats the request to the latest version of default service by
    replacing all occurrences of the hostname to the new_host defined
    above. The replacement happens for:
      - URL and URL query string
      - Headers, including cookie headers
      - The body, if we can decode it.=
    Additionally:
      - All headers starting with 'X-' are removed (to not mess-up with
        Google's reverse proxies)
      - The X-OAuth-Redirect header is added, containing the old hostname
    """
    if flask.request.scheme == 'http':
        flask.abort(400, 'Only HTTPS is supported.')

    old_host = flask.request.host

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
