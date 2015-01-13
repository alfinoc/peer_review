from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest
from persistent import RedisStore
from json import loads, dumps

def missingParams(actual, required):
   notFound = filter(lambda p : not p in actual, required)
   if len(notFound) > 0:
      notFound = map(lambda s : '"' + s + '"', notFound)
      return BadRequest('Required parameters: ' + (', '.join(notFound)))
   return None

def subset(dict, keys):
   res = {}
   for k in keys:
      res[k] = dict[k]
   return res

class PeerReviewService(object):
   def get_survey(self, request):
      missing = missingParams(request.args, ['assignment'])
      print missing
      if missing != None:
         return missing

      # TODO: check auth and assigned
      
      # Get assignment information.
      assignment = self.store.getAssignment(request.args['assignment'])
      questions = map(self.store.getQuestion, loads(assignment['questions']))
      questions = map(lambda q : subset(q, ['prompt']), questions)

      # Get course information if requested.
      course = ''
      if 'course' in request.args:
         course = self.store.getCourse(request.args['course'])
         if course != None:
            course = course['title']

      return self.render('assignment.html',
                          name=assignment['title'],
                          course=course,
                          questions=questions)

   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/survey', endpoint='survey'),
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
