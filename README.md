Staging Environment for App Engine using Python
===============================================

This is the repo used for [my blog](https://yannick.clybouw.eu/blog) and 
features a staging environment on Google App Engine:

  - We use a non-promoted service version for staging, so you can easily move a
    version from staging to production by simply changing the traffic 
    allocation of the App Engine.
  - The application requires to be reachable on a fixed HTTPS URL (e.g. needed 
    for OAuth with fixed redirect_url + SSL).
    
We will implement this staging environment by using a transparent reverse proxy
running as a separate service in the App Engine Standard Environment. We use
the Python [Flask web framework](https://flask.palletsprojects.com) for this.

There is an example app provided using Google as OAuth2 identity provider. Once
logged in, you can view your Google profile (name and picture). The app is a 
Flask application running on Google App Engine Standard Environment.


Prerequisites
=============

Before starting:

  - Make sure you have [set up a Google Cloud project for App Engine](https://cloud.google.com/appengine/docs/standard/python3/quickstart#before-you-begin)
  - Have this repository checked out locally
  - Have Python 3.7 or newer
  - Have docker and docker-compose


Setting-Up the Example App
==========================

Create OAuth2 Credentials
-------------------------

We need a OAuth2 Client ID and Client Secret for our application. 

1.  Go to [Credentials Page on the Google Cloud Console](https://console.developers.google.com/apis/credentials)
2.  Click on Create credentials > OAuth client ID
3.  Select Web application and fill in the form:
      - Name: e.g. flask-oauth
      - Authorized JavaScript origins: can be left empty
      - Authorized redirect URIs (replace "yourproject" with your actual
        Google Cloud project name):
        - http://127.0.0.1:5000/google/authorize
        - https://yourproject.appspot.com/google/authorize
        - https://staging-dot-yourproject.appspot.com/google/authorize
4.  The returned client ID should be stored in `settings.py`.
5.  Create a new file `settings.py` and add the client secret:
    ```python
    GOOGLE_CLIENT_SECRET = 'your_client_secret'
    ```

Run the Flask Application
-------------------------

1.  Within the `example_app` directory, create a virtual environment with all 
    required packages:
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
3.  Once deployed, you can reach it on https://yourproject.appspot.com. Try if 
    the Google OAuth flow works by clicking on "click here to see your Google 
    Profile".
4.  Change something in `main.py`, example some strings within the HTML. Deploy 
    a new version without promoting it. We will use this version for our 
    staging environment:
    ```bash
    gcloud app deploy
    ```
5.  On the [versions page of the Google Cloud Console](https://console.cloud.google.com/appengine/versions)
    you will see the new version with status `serving`, but with 0% traffic 
    allocation.
    
When clicking on the version, you are redirected to 
https://yourversion-dot-yourproject.appspot.com. The index page will work
(takes a few second due to the cold start), but the OAuth flow will fail, 
because this URL is not an accepted redirect_uri configured for our Client ID.

To fix the OAuth flow, we could add the version URL each time to list of 
"Authorized redirect URIs", but this is quite cumbersome. We use now Google as
an example, where this could be feasible, but other identity providers might 
not be that flexible: some smaller providers have only a manual process in 
place where you have to send an e-mail to their sysadmin.

In next section, we will describe how we will make this new version accessible
at https://staging-dot-yourproject.appspot.com.
    

Setting-Up the Staging Environment
==================================

In the root app-engine-staging directory, execute:
```bash
gcloud app deploy --promote
```

On the [services page of the Google Cloud Console](https://console.cloud.google.com/appengine/services)
you will see a new service named `staging`. When clicking on it, you are 
redirected to https://staging-dot-yourproject.appspot.com. The index page will 
work (takes a few second due to the cold start), as well the OAuth flow! You
should notice that the changes of step 4 of previous section are shown here,
meaning you are using the not promoted version!

To know how this work, you can have a peak at [main.py](main.py).

Note that if you deploy a new version of your default service, staging will 
only updated after a fresh start. You can either wait for 10 minutes since last
request to staging (see [app.yaml](app.yaml)) or manually do a stop and start
of the staging service on the [versions page of the Google Cloud Console](https://console.cloud.google.com/appengine/versions).


Handling Server-to-Server Requests
==================================

There is one big catch: the `staging` service behaves as a reverse proxy 
between your browser and the `default` service, but has no impact of the 
requests between the `default` service and an external party.

Example in case of OAuth2: we need to exchange a code to an access token and 
within that request we need to provide the redirect_uri. To solve this, our
`staging` service will add a header `X-OAuth-Redirect` containing the original
hostname (in this case staging-dot-myproject.appspot.com). The example app has
been adjusted to take care of this behaviour.
