from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from werkzeug.utils import redirect
from werkzeug.contrib.securecookie import SecureCookie
from persistent import RedisStore
from json import loads, dumps
from session import SessionRequest
import forms
import model

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
   def get_add(self, request):
      return Response(dumps({
         'new': {
            'name': 'a new one!',
            'questions': [],
            'revision': '1000:asst'
         }
      }))

   def get_remove(self, request):
      return Response('yeah, you betcha')

   def get_revise(self, request):
      # Authenticate
      if not self.store.isInstructor(request.user):
         return Unauthorized('Sign in as an instructor to edit survey details.')

      if request.method != 'GET':  # TODO:change back
         return BadRequest('POST request required')

      # Validate
      form = forms.ChangeForm(request.args)  #TODO: change back
      if not form.validate():
         return BadRequest(form.errors);
      if form.store_key.data not in self.store:
         return BadRequest('unknown store_key')

      # Change hash_key's value and store the revision.
      key = form.hash_key.data
      value = form.hash_value.data
      entry = self.store.getAgnostic(form.store_key.data)()
      if key != None:
         entry[key] = value
      self.store.reviseEntry(entry)
      return Response(dumps({ 'new': str(value) }))

   def get_survey_submit(self, request):
      args = request.form
      missing = missingParams(args, ['assignment'])
      if missing != None:
         return missing
      # TODO: check auth and assigned
      for questionKey in set(args) - set(['assignment']):
         value = args[questionKey].strip()
         if value == '':
            continue
         question = self.store.getQuestion(questionKey)
         if question == None:
            return BadRequest('Question with id {0} not defined.'.format(questionKey))
         self.store.addAnswer(question, Answer(value))
      return Response('Successfully recorded responses.')

   def get_survey(self, request):
      missing = missingParams(request.args, ['assignment'])
      if missing != None:
         return missing

      # TODO: check auth and assigned

      def getQuestion(questionKey):
         dict = self.store.getQuestion(questionKey)
         return dict

      # Get assignment information.
      assignment = self.store.getAssignment(request.args['assignment'])
      questions = map(getQuestion, loads(assignment['questions']))

      # Get course information if requested.
      course = ''
      if 'course' in request.args:
         course = self.store.getCourse(request.args['course'])
         if course != None:
            course = course['title']

      return self.render('assignment.html', name=assignment['title'],
                         course=course, questions=questions)

   def get_dashboard(self, request):
      login = self.login_check(request)
      if login != None:
         return login

      if self.store.isInstructor(request.user):
         assignments = self.store.getAllAssignments()
         for a in assignments:
            a.questions = map(self.store.getQuestion, loads(a.questions))
         return self.render('prof_dashboard.html', assignments=assignments)
      else:
         return Response("You're a student (%s)" % request.user)

   # Returns None if logged in or request contains correct username/password
   # combo. In the latter case, user is logged in. Otherwise, returns the
   # login page with an error displayed.
   def login_check(self, request):
      if not request.logged_in:
         form = request.form
         missing = missingParams(form, ['username', 'password'])
         if missing == None:
            request.logout()
            username = form.get('username')
            password = form.get('password')
            if self.store.passwordMatches(username, password):
               request.login(username)
               return None
         return self.get_login(request, True)
      return None

   def get_login(self, request, error=False):
      return self.render('login.html', error=error)

   def get_logout(self, request):
      request.logout()
      return self.get_login(request)

   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/add', endpoint="add"),
         Rule('/revise', endpoint="revise"),
         Rule('/survey/submit', endpoint="survey_submit"),
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
