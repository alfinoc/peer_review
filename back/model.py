from json import dumps

def _suffix(s, suffix):
   return str(s) + ':' + str(suffix)

class StoreEntry:
   def __init__(self):
      self._serializable = []
      self.id = None
      self.typeKey = None

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
      if self.typeKey == None:
         raise NotImplementedError('No store type key (suffix) for base entry.')
      return self.typeKey

   def key(self):
      if self.id == None:
         raise NotImplementedError('No store key for base entry.')
      return _suffix(self.id, self.typeKey)

   def loadHash(self, hash):
      for key in hash:
         self.addSerialProperty(key, hash[key])

class Course(StoreEntry):
   def __init__(self, title='Untitled', assignments=[], participants=[]):
      StoreEntry.__init__(self)
      self.typeKey = 'course'
      self.addSerialProperty('title', title)
      self.addSerialProperty('assignments', assignments)
      self.addSerialProperty('participants', participants)

class Assignment(StoreEntry):
   def __init__(self, title='Untitled', questions=[], users=[]):
      StoreEntry.__init__(self)
      self.typeKey = 'asst'
      self.addSerialProperty('title', title)
      self.addSerialProperty('questions', questions)
      self.addSerialProperty('assigned', users)

class Question(StoreEntry):
   def __init__(self, prompt='Question Prompt'):
      StoreEntry.__init__(self)
      self.typeKey = 'quest'
      self.addSerialProperty('prompt', prompt)
      self.addSerialProperty('answers', [])

class Answer(StoreEntry):
   def __init__(self, text='', value=None):
      StoreEntry.__init__(self)
      self.suffix = 'answer'
      self.addSerialProperty('text', text)
      self.addSerialProperty('value', value)
