import secrets

SECRET_KEY = secrets.SECRET_KEY

GOOGLE_CLIENT_ID = '306862382061-mrjfnk6bjulvmvp44g19fkqktoor8er8.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = secrets.GOOGLE_CLIENT_SECRET
GOOGLE_ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_API_BASE_URL = 'https://www.googleapis.com/'
GOOGLE_CLIENT_KWARGS = {'scope': 'profile'}
