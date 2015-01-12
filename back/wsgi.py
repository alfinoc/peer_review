import os
from service import PeerReviewService
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   app = PeerReviewService()
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/assignment': os.path.join(os.path.dirname(__file__), '../front/assignment.html'),
      '/global':  os.path.join(os.path.dirname(__file__), '../front/global'),
      '/components':  os.path.join(os.path.dirname(__file__), '../front/components'),
   })
   return app