Flask - OAuth2 - Google App Engine
==================================

This is the repo used for [my blog](https://yannick.clybouw.eu/blog) and 
features following:

  - Flask application
  - Google App Engine Standard Environment
  - Use non-promoted service version as a staging environment
  - App contains a OAuth2 flow with redirect_uri set at the identity provider
  - A simple reverse proxy service for staging

This example app uses Google as identity provider. Once logged in, you can 
view your Google profile (name and picture).


Prerequisites
-------------

Before starting:

  - Make sure you have [set up a Google Cloud project for App Engine](https://cloud.google.com/appengine/docs/standard/python3/quickstart#before-you-begin)
  - Have a domain name (I use clybouw.eu)
  - Have this repository checked out locally
  - Have Python 3.7 or newer
  - Have docker and docker-compose


Verify your domain at Google
----------------------------

Go to [Webmaster Central](https://www.google.com/webmasters/verification/) and
add your domain as property. You can only proceed this tutorial once your
domain has been verified.


Create OAuth2 Credentials
-------------------------

We need a OAuth2 Client ID and Client Secret for our application. 

1.  Go to [Credentials Page on the Google Cloud Console](https://console.developers.google.com/apis/credentials)
2.  Click on Create credentials > OAuth client ID
3.  Select Web application and fill in the form:
      - Name: e.g. flask-oauth
      - Authorized JavaScript origins: can be left empty
      - Authorized redirect URIs:
        - http://127.0.0.1:5000/google/authorize
        - https://flask-oauth.yourdomain.com/google/authorize
        - https://flask-oauth-staging.yourdomain.com/google/authorize
        - https://staging.flask-oauth.yourdomain.com/google/authorize
4.  The returned client ID should be stored in `settings.py`.
5.  Create a new file `settings.py` and add the client secret:
    ```python
    GOOGLE_CLIENT_SECRET = 'your_client_secret'
    ```


Run the Flask Application
-------------------------

1.  Within this directory, create a virtual environment with all required 
    packages:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  Generate secret key to sign your session cookie. Execute in your shell:
    ```bash
    python -c 'import os; print(os.urandom(16))'
    ```
    The result looks like `b'_5#y2L"F4Q8z\n\xec]'`. Add this to your 
    `secrets.py` file, e.g.:
    ```python
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]'
    GOOGLE_CLIENT_SECRET = 'your_client_secret'
    ```
3.  Finally, run the application locally:
    ```bash
    FLASK_APP=main.py FLASK_ENV=DEVELOPMENT FLASK_DEBUG=1 python -m flask run
    ```
    The application runs now on [http://127.0.0.1:5000/].
4.  Try if the Google OAuth flow works by clicking on "click here to see your 
    Google Profile".


Deploying to the Google App Engine
----------------------------------

1.  To avoid auto-promote when doing `gcloud app deploy`, we need to set:
    ```bash
    gcloud config set app/promote_by_default false
    ```
    This only needs to be done once.
2.  To deploy a first time, please run:
    ```bash
    gcloud app deploy --promote
    ```
3.  Once deployed, you can reach it on https://yourproject.appspot.com. The
    index page will be reachable (takes a few second due to the cold start).
    The OAuth flow will fail, because this URL is not an accepted redirect_uri
    configured for our Client ID.
    

Adding Your Domain to Your App
------------------------------

In the Google Cloud Console, on the 
[settings page of the App Engine](https://console.cloud.google.com/appengine/settings/domains)
you can add the custom domain flask-oauth.yourdomain.com with automatic SSL.
It can take a while to be completed. Once finished, you can browse to
[https://flask-oauth.yourdomain.com] and click on the link. The OAuth flow
should work now, as it worked locally.


Deploy a Staging Environment
----------------------------

Execute:
```bash
gcloud app deploy
```

On the [versions page of the Google Cloud Console](https://console.cloud.google.com/appengine/versions)
you will see the new version with status `serving`, but with 0% traffic 
allocation. When clicking on the version, you are redirected to 
`https://yourversion-dot-yourproject.appspot.com`. The index page will work,
but the OAuth flow won't.

To fix the OAuth flow, we could add the version URL each time to list of 
"Authorized redirect URIs", but this is quite cumbersome. We use now Google as
an example, where this could be feasible, but other identity providers might 
not be that flexible: some smaller providers have only a manual process in 
place where you have to send an e-mail to their sysadmin.

To have a permanent fix, please proceed this README.


Setting-Up a Transparent Forward Proxy
--------------------------------------

<!---
TODO: 
  - add custom domain (or fix docs for appspot.com)
  - auto-select staging version
  - write this section.
-->
