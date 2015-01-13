from os import path 
from service import PeerReviewService
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   currPath = path.dirname(__file__)
   template_path = path.join(currPath, '../front/templates')
   app = PeerReviewService(template_path)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/global':  path.join(currPath, '../front/global'),
      '/components':  path.join(currPath, '../front/components'),
   })
   return app