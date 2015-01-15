from werkzeug.wrappers import Request
from werkzeug.utils import cached_property
from werkzeug.contrib.securecookie import SecureCookie

# os.urandom(20)
SECRET_KEY = '\xd8W\xc4\x12s\x83\xf8F\x81\xa9\xb3}\xbb\x06H\xc5#\x8f\xc8C'
COOKIE_NAME = 'session'
USER_KEY = 'username'

"""
A request with a secure cookie session.
See: https://github.com/mitsuhiko/werkzeug/blob/master/examples/cookieauth.py
"""
class SessionRequest(Request):
   """Log the user out."""
   def logout(self):
      self.session.pop(USER_KEY, None)

   """Log the user in."""
   def login(self, username):
      self.session[USER_KEY] = username

   """Is the user logged in?"""
   @property
   def logged_in(self):
      return self.user is not None

   """The user that is logged in."""
   @property
   def user(self):
      return self.session.get(USER_KEY)

   @cached_property
   def session(self):
      data = self.cookies.get(COOKIE_NAME)
      if not data:
         return SecureCookie(secret_key=SECRET_KEY)
      return SecureCookie.unserialize(data, SECRET_KEY)
