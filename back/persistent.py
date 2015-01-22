from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt
from bisect import bisect_left
from json import loads, dumps
import redis

HOST = 'localhost'
PORT = '6379'

class StoreEntry:
   def __init__(self):
      self._serializable = []

   def hash(self):
      res = {}
      for prop in self._serializable:
         value = getattr(self, prop)
         if type(value) == dict or type(value) == list:
            value = dumps(value)
         res[prop] = value
      return res

   def addSerialProperty(self, name, value):
      setattr(self, name, value)
      self._serializable.append(name)

   # TODO: the getters below should ideally return a the storeentry subclasses
   # below. this probably means adding IDs to storeentries when they're added,
   # and also including the id in the store entry object on return
   def fromHash(subclass, hash, id=None):
      entry = subclass()
      return entry

class Course(StoreEntry):
   def __init__(self, title='Untitled', assignments=[], participants=[]):
      StoreEntry.__init__(self)
      self.addSerialProperty('title', title)
      self.addSerialProperty('assignments', assignments)
      self.addSerialProperty('participants', participants)

class Assignment(StoreEntry):
   def __init__(self, title='Untitled', questions=[], users=[]):
      StoreEntry.__init__(self)
      self.addSerialProperty('title', title)
      self.addSerialProperty('questions', questions)
      self.addSerialProperty('assigned', users)

class Question(StoreEntry):
   def __init__(self, prompt='Question Prompt'):
      StoreEntry.__init__(self)
      self.addSerialProperty('prompt', prompt)
      self.addSerialProperty('answers', [])

class Answer(StoreEntry):
   def __init__(self, text='', value=None):
      StoreEntry.__init__(self)
      self.addSerialProperty('text', text)
      self.addSerialProperty('value', value)

"""
Key scheme:
   all_courses -> list(id)
   <id>:course -> CourseHash
   <id>:asst -> AssignmentHash
   <id>:quest -> QuestionHash
   <id>:answer -> AnswerHash
"""
def _suffix(s, suffix):
   return str(s) + ':' + str(suffix)

class RedisStore:
   def __init__(self):
      try:
         self.store = redis.Redis(HOST, port=PORT)
      except redis.ConnectionError:
         raise IOError

   def addUser(self, username, password, isInstructor=False, name='Anonymous', email=''):
      passKey = _suffix(username, 'password')
      if self.store.exists(passKey):
         raise ValueError('User (%s) already exists.' % username)
      self.store.set(passKey, sha256_crypt.encrypt(password))
      self.store.hmset(_suffix(username, 'user'),  {
         'name': name,
         'email': email,
         'instructor': isInstructor
      })

   def isInstructor(self, username):
      return self.store.hget(_suffix(username, 'user'), 'instructor') == 'True'

   def isStudent(self, username):
      return not self.isInstructor(username)

   def passwordMatches(self, username, password):
      key = _suffix(username, 'password')
      if self.store.exists(key):
         return pwd_context.verify(password, self.store.get(key))
      return False

   def addCourse(self, course):
      course_id = self._setEntry('course', course)
      self.store.rpush('all_courses', course_id)
      return course_id

   def addAssignment(self, course_id, assignment):
      newAsst = self._setEntry('asst', assignment)
      self._pushToHashList(_suffix(course_id, 'course'), 'assignments', newAsst)
      return newAsst

   def addQuestion(self, assignment_id, question):
      newQuestion = self._setEntry('quest', question)
      self._pushToHashList(_suffix(assignment_id, 'asst'), 'questions', newQuestion)
      return newQuestion

   def addAnswer(self, question_id, answer):
      newAnswer = self._setEntry('answer', answer)
      self._pushToHashList(_suffix(question_id, 'quest'), 'answers', newAnswer)
      return newAnswer

   def getCourse(self, course_id):
      return self._getEntry(course_id, 'course')

   def getAssignment(self, assignment_id):
      return self._getEntry(assignment_id, 'asst')

   def getQuestion(self, question_id):
      return self._getEntry(question_id, 'quest')

   def getAnswer(self, answer_id):
      return self._getEntry(answer_id, 'answer')

   def _getEntry(self, id, suffix):
      hashValue = self.store.hgetall(_suffix(id, suffix))
      return hashValue if len(hashValue) != 0 else None

   def _setEntry(self, suffix, entry):
      nextId = self._getNewId(suffix)
      self.store.hmset(_suffix(nextId, suffix), entry.hash())
      return nextId

   def _getNewId(self, suffix):
      return self.store.incr(_suffix('last_term_id', suffix))

   def _pushToHashList(self, hashKey, listKey, value):
      prev = loads(self.store.hget(hashKey, listKey))
      prev.append(value)
      self.store.hset(hashKey, listKey, prev)
