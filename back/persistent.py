from bisect import bisect_left
from json import loads
import redis

HOST = 'localhost'
PORT = '6379'

class StoreEntry:
   def asDict(self):
      res = {}
      for prop in self._serializable:
         res[prop] = getattr(self, prop)
      return res

   def addSerialProperty(self, name, value):
      if not hasattr(self, '_serializable'):
         self._serializable = []
      setattr(self, name, value)
      self._serializable.append(name)

class Course(StoreEntry):
   def __init__(self, title='Untitled', assignments=[], participants=[]):
      self.addSerialProperty('title', title)
      self.addSerialProperty('assignments', assignments)
      self.addSerialProperty('participants', participants)

class Assignment(StoreEntry):
   def __init__(self, title='Untitled', questions=[]):
      self.addSerialProperty('title', title)
      self.addSerialProperty('questions', questions)

class Question(StoreEntry):
   def __init__(self, prompt='Question Prompt'):
      self.addSerialProperty('prompt', prompt)
      self.addSerialProperty('responses', [])

class Response(StoreEntry):
   def __init__(self, text='', value=None):
      self.addSerialProperty('text', text)
      self.addSerialProperty('value', value)

"""
Key scheme:
   all_courses -> list(id)
   <id>:course -> CourseHash
   <id>:asst -> AssignmentHash
   <id>:quest -> QuestionHash
   <id>:resp -> ResponseHash
"""
def _suffix(self, str, suffix):
   return str + ':' + suffix

class RedisStore:
   def __init__(self):
      try:
         self.store = redis.Redis(HOST, port=PORT)
      except redis.ConnectionError:
         raise IOError

   def addCourse(self, course):
      return self._setEntry(self, 'course', course)

   def addAssignment(self, course_id, assignment):
      newAsst = self._setEntry(self, 'asst', assignment)
      self._pushToHashList(_suffix(course_id, 'course'), 'assignments', newAsst)
      return newAsst

   def addQuestion(self, assignment_id, question):
      newQuestion = self._setEntry(self, 'quest', question)
      self._pushToHashList(_suffix(course_id, 'asst'), 'questions', newQuestion)
      return newQuestion

   def addResponse(self, response):
      newResponse = self._setEntry(self, 'resp', response)
      self._pushToHashList(_suffix(course_id, 'quest'), 'responses', newResponse)
      return newResponse

   def getCourse(self, course_id):
      return self._getEntry(course_id, 'course')

   def getAssignment(self, assignment_id):
      return self._getEntry(assignment_id, 'asst')

   def getQuestion(self, question_id):
      return self._getEntry(question_id, 'asst')

   def getResponse(self, response_id):
      return self._getEntry(response_id, 'asst')

   def _getEntry(self, suffix, id):
      self.store.hgetall(_suffix(id, suffix))

   def _setEntry(self, suffix, entry):
      nextId = self._getNewId(suffix)
      self.store.hmset(_suffix(nextId, suffix), entry.asDict())
      return nextId

   def _getNewId(self, suffix):
      return self.store.incr(_suffix('last_term_id', suffix))

   def _pushToHashList(self, hashKey, listKey, value):
      prev = loads(self.store.hget(course_key, listKey))
      prev.append(value)
      self.store.hset(course_key, listKey, prev)
