from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt
from bisect import bisect_left
from json import loads
from functools import partial
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

   def __contains__(self, key):
      return self.store.exists(key)

   def addUser(self, username, password, isInstructor=False, name='Anonymous', email=''):
      key = _suffix(username, 'user')
      if self.store.exists(key):
         raise ValueError('User (%s) already exists.' % username)
      self.store.hmset(key, {
         'name': name,
         'email': email,
         'instructor': isInstructor,
         'password': sha256_crypt.encrypt(password)
      })

   def isInstructor(self, username):
      return self.store.hget(_suffix(username, 'user'), 'instructor') == 'True'

   def isStudent(self, username):
      return not self.isInstructor(username)

   def passwordMatches(self, username, password):
      key = _suffix(username, 'user')
      if self.store.exists(key):
         return pwd_context.verify(password, self.store.hget(key, 'password'))
      return False

   # Setters/adders.
   def addCourse(self, course):
      self._addNewEntry(course)
      self.store.rpush('all_courses', course.getId())

   def addAssignment(self, assignment, course=None):
      course = course or self._getEntry(Course, assignment.parent())
      self._registerEntry(course, assignment, 'assignments')

   def addQuestion(self, question, assignment=None):
      self._registerEntry(assignment, question, 'questions')

   def addAnswer(self, answer, question=None):
      self._registerEntry(question, answer, 'answers')

   # Getters.
   def getCourse(self, id):
      return self._getEntry(Course, id)

   def getAssignment(self, id):
      return self._getEntry(Assignment, id)

   def getQuestion(self, id):
      return self._getEntry(Question, id)

   def getAnswer(self, id):
      return self._getEntry(Answer, id)

   def guessAccessors(self, key):
      try:
         id, suffix = key.split(':')
         id = int(id)
      except:
         raise ValueError('illegal key format')
      get, set = self._accessors(suffix)
      return (partial(get, id), partial(set, id))

   def _accessors(self, suffix):
      accessors = {
         Course.typeSuffix: (self.getCourse, self.addCourse),
         Assignment.typeSuffix: (self.getAssignment, self.addAssignment),
         Question.typeSuffix: (self.getQuestion, self.addQuestion),
         Answer.typeSuffix: (self.getAnswer, self.addAnswer)
      }
      if suffix not in accessors:
         raise ValueError('unknown suffix')
      return accessors[suffix]

   def getAllCourses(self):
      return map(self.getCourse, self.store.lrange('all_courses', 0, -1))

   def getAllAssignments(self):
      courses = self.getAllCourses()
      assignments = []
      for c in courses:
         assignments += map(self.getAssignment, loads(c.assignments))
      return assignments

   def _getEntry(self, constructor, id):
      entry = constructor()
      entry.setId(id)
      hash = self.store.hgetall(entry.key())
      if len(hash) != 0:
         entry.loadHash(hash)
         return entry
      else:
         return None

   # Adds the new 'childEntry'. 'parentEntry' should be already stored. parent is
   # recorded in child hash, and child id is pushed to the child list at key
   # 'parentListKey' on the parent.
   # Raises ValueError if 'parentEntry' is not stored.
   def _registerEntry(self, parentEntry, childEntry, parentListKey):
      if parentEntry.getId() == None:
         raise ValueError('Parent entry (%s) not stored.' % str(type(parentEntry)))      

      childEntry.setParentKey(parentEntry.key())
      self._addNewEntry(childEntry)
      self._pushToHashList(parentEntry.key(), parentListKey, childEntry.getId())

   # Records the entry as a revision with the same id given in 'entry'. The old
   # entry previously corresponding to 'entry's id is given a new id which is stored
   # in 'entry's revision precedessor field.
   # Raises ValueError if 'entry' is not stored.
   def reviseEntry(self, entry):
      # An entry with the current ID exists, so make a revision. Store
      # the revision predecessor and guarantee that the current ID now
      # refers to the new entry (argument).
      if not self.store.exists(entry.key()):
         raise ValueError('%s entry (%d) not stored.' % (r.suffix(), r.getId()))
      suffix = entry.suffix()

      # Generate a new ID setup for the currently stored version of entry.
      newId = self._getNewId(suffix)
      newKey = _suffix(newId, suffix)
      entry.setRevisionPredecessor(newId)
      newHash = entry.hash()

      # Gather old ID setup to associate with entry.
      oldId = entry.getId()
      oldKey = entry.key();
      oldHash = self.store.hgetall(oldKey)

      self.store.hmset(oldKey, newHash)
      self.store.hmset(newKey, oldHash)

   def _pushToHashList(self, hashKey, listKey, value):
      prev = loads(self.store.hget(hashKey, listKey))
      prev.append(value)
      self.store.hset(hashKey, listKey, prev)

   def _addNewEntry(self, entry):
      entry.setId(self._getNewId(entry.suffix()))
      self.store.hmset(entry.key(), entry.hash())

   def _getNewId(self, suffix):
      return self.store.incr(_suffix('last_term_id', suffix))
