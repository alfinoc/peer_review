from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest
from werkzeug.utils import redirect
from werkzeug.contrib.securecookie import SecureCookie
from persistent import RedisStore, Answer
from json import loads, dumps
from session import SessionRequest

HACKY_DUMMY = {
   'user': 'password',
   'admin': 'lol'
}

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
   def get_respond_survey(self, request):
      args = request.form
      missing = missingParams(args, ['assignment'])
      if missing != None:
         return missing
      # TODO: check auth and assigned
      for questionKey in set(args) - set(['assignment']):
         value = args[questionKey].strip()
         if value == '':
            continue
         if self.store.getQuestion(questionKey) == None:
            return BadRequest('Question with id {0} not defined.'.format(questionKey))
         self.store.addAnswer(questionKey, Answer(value))
      return Response('Successfully recorded responses.')

   def get_survey(self, request):
      missing = missingParams(request.args, ['assignment'])
      print missing
      if missing != None:
         return missing

      # TODO: check auth and assigned

      def getQuestionWithKey(questionKey):
         print questionKey
         dict = self.store.getQuestion(questionKey)
         dict['key'] = questionKey
         return dict

      # Get assignment information.
      assignment = self.store.getAssignment(request.args['assignment'])
      questions = map(getQuestionWithKey, loads(assignment['questions']))

      # Get course information if requested.
      course = ''
      if 'course' in request.args:
         course = self.store.getCourse(request.args['course'])
         if course != None:
            course = course['title']

      return self.render('assignment.html', name=assignment['title'],
                         course=course, questions=questions)

   def get_dashboard(self, request):
      if not request.logged_in:
         form = request.form
         missing = missingParams(form, ['username', 'password'])
         if missing != None:
            return self.get_login('login.html')
         username = form.get('username')
         password = form.get('password')
         if username in HACKY_DUMMY and HACKY_DUMMY[username] == password:
            request.login(username)
         else:
            return self.get_login(request, True)

      if request.logged_in:
         return Response("Logged in as " + request.user)
      else:
         return self.get_login('login.html', True)

   def get_login(self, request, error=False):
      return self.render('login.html', error=error)

   def get_logout(self, request):
      request.logout()
      return self.get_login(request)

   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/respond/survey', endpoint="respond_survey"),
         Rule('/dashboard', endpoint='dashboard'),
         Rule('/survey', endpoint='survey'),
         Rule('/logout', endpoint='logout'),
         Rule('/', endpoint='login'),
         Rule('/<all>', redirect_to='/dashboard'),
      ])
      self.store = RedisStore()
      self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                   autoescape=True)

   def wsgi_app(self, environ, start_response):
      request = SessionRequest(environ);
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
         response = getattr(self, 'get_' + endpoint)(request, **values)
         request.session.save_cookie(response);
         return response
      except HTTPException, e:
         return e
