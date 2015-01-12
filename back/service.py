from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest
from persistent import RedisStore

def missingParams(actual, required):
   return filter(lambda p : not p in required, actual)
   if len(notFound) > 1:
      return BadRequest('Required parameters: ' + (', '.join(params)))
   notFound = map(lambda s : '"' + s + '"', notFound)
   return None

class PeerReviewService(object):
   def get_assignment_page(self, request):
      missing = missingParams(request.args, ['assignment'])
      if missing != None:
         return missing
      # TODO: check auth and assigned
      return self.render('assignment.html', request.args['assignment'])

   def get_assignment_data(self, request):
      if not 'assignment' in request.args:
         return requiredParameterError(['assignment'])
      # TODO: check auth and assigned
      questions = [{'id': 1, 'prompt': 'heh'}]
      course = {'id': 2, 'name': 'phil 101'}

      return self.render('templates/survey.js', course=course, questions=questions,
                         name="assignment 7")

   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/assignment', endpoint='assignment_page'),
         Rule('/survey', endpoint='assignment_data'),
         Rule('/<all>', redirect_to='/'),
      ])
      self.store = RedisStore()
      self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                   autoescape=True)

   def wsgi_app(self, environ, start_response):
      request = Request(environ);
      response = self.dispatch_request(request);
      return response(environ, start_response);

   def render(self, template_name, **context):
      t = self.jinja_env.get_template(template_name)
      return Response(t.render(context), mimetype='text/html')

   def __call__(self, environ, start_response):
      return self.wsgi_app(environ, start_response)

   def dispatch_request(self, request):
      adapter = self.url_map.bind_to_environ(request.environ)
      try:
         endpoint, values = adapter.match()
         return getattr(self, 'get_' + endpoint)(request, **values)
      except HTTPException, e:
         return e
