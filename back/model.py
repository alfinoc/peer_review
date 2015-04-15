from json import dumps

def _suffix(s, suffix):
   return str(s) + ':' + str(suffix)

class StoreEntry:
   typeSuffix = None
   noneAble = ['parent', 'last']

   def __init__(self):
      self.id = None
      self._serializable = []
      for key in self.noneAble:
         self.addSerialProperty(key, None)

   def setParentKey(self, key):
      self.parent = key

   def setRevisionPredecessor(self, id):
      self.last = id

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

   def setId(self, id):
      self.id = id

   def getId(self):
      return self.id

   def suffix(self):
      if self.typeSuffix == None:
         raise NotImplementedError('No store type key (suffix) for base entry.')
      return self.typeSuffix

   def key(self):
      if self.id == None:
         raise NotImplementedError('No store key for base entry.')
      return _suffix(self.id, self.typeSuffix)

   def loadHash(self, hash):
      for key in self.noneAble:
         if hash[key] == 'None':
            hash[key] = None
      for key in hash:
         self.addSerialProperty(key, hash[key])
      return self

   def __getitem__(self, key):
      if key not in self._serializable:
         raise KeyError()
      return getattr(self, key)

   def __setitem__(self, key, value):
      if key not in self._serializable:
         raise KeyError()
      return setattr(self, key, value)

   def revise(self, store):
      store.reviseEntry(self)

class Course(StoreEntry):
   typeSuffix = 'course'
   def __init__(self, title='Untitled', assignments=[], participants=[]):
      StoreEntry.__init__(self)
      self.addSerialProperty('title', title)
      self.addSerialProperty('assignments', assignments)
      self.addSerialProperty('participants', participants)

   def add(self, store):
      store._registerCourse(self)

class Assignment(StoreEntry):
   typeSuffix = 'asst'
   def __init__(self, title='Untitled', questions=[], assigned=[]):
      StoreEntry.__init__(self)
      self.addSerialProperty('title', title)
      self.addSerialProperty('questions', questions)
      self.addSerialProperty('assigned', assigned)

   def add(self, course, store):
      store._registerEntry(course, self, 'assignments')

class Question(StoreEntry):
   typeSuffix = 'quest'
   def __init__(self, prompt='Question Prompt'):
      StoreEntry.__init__(self)
      self.addSerialProperty('prompt', prompt)
      self.addSerialProperty('answers', [])

   def add(self, assignment, store):
      store._registerEntry(assignment, self, 'questions')

class Answer(StoreEntry):
   typeSuffix = 'answer'
   def __init__(self, text='', value=None):
      StoreEntry.__init__(self)
      self.addSerialProperty('text', text)
      self.addSerialProperty('value', value)

   def add(self, question, store):
      store._registerEntry(question, self, 'answers')
