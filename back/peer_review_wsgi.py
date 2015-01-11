import os
from service import PeerReviewService
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   app = PeerReviewService()
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {})
   return app