from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt
from bisect import bisect_left
from json import loads
import redis

from model import Course, Assignment, Question, Answer

HOST = 'localhost'
PORT = '6379'

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
      # TODO: make password a key in this hash

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
      course.setId(course_id)

   def addAssignment(self, course, assignment):
      self._registerEntry(course, assignment, 'assignments')

   def addQuestion(self, assignment, question):
      self._registerEntry(assignment, question, 'questions')

   def addAnswer(self, question, answer):
      self._registerEntry(question, answer, 'answers')

   def getCourse(self, id):
      return self._getEntry(Course, id)

   def getAssignment(self, id):
      return self._getEntry(Assignment, id)

   def getQuestion(self, id):
      return self._getEntry(Question, id)

   def getAnswer(self, id):
      return self._getEntry(Answer, id)

   def _getEntry(self, constructor, id):
      entry = constructor()
      entry.setId(id)
      hash = self.store.hgetall(entry.key())
      if len(hash) != 0:
         entry.loadHash(hash)
         return entry
      else:
         return None

   def _setEntry(self, suffix, entry):
      nextId = self._getNewId(suffix)
      self.store.hmset(_suffix(nextId, suffix), entry.hash())
      return nextId

   # Stores both entries if they aren't stored already, and pushes childEntry's id
   # to the list in parentEntry's hash keyed on parentListKey.
   def _registerEntry(self, parentEntry, childEntry, parentListKey):
      if parentEntry.getId() == None:
         raise ValueError('Parent entry (%s) not stored.' % str(type(parentEntry)))
      if childEntry.getId() == None:
         self._storeEntry(childEntry)
      self._pushToHashList(parentEntry.key(), parentListKey, childEntry.getId())

   def _storeEntry(self, entry):
      entry.setId(self._getNewId(entry.suffix()))
      self.store.hmset(entry.key(), entry.hash())

   def _pushToHashList(self, hashKey, listKey, value):
      prev = loads(self.store.hget(hashKey, listKey))
      prev.append(value)
      self.store.hset(hashKey, listKey, prev)

   def _getNewId(self, suffix):
      return self.store.incr(_suffix('last_term_id', suffix))
