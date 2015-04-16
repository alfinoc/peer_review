from werkzeug.wrappers import Request, Response
from json import dumps
import model

def validate_form(form, store, keys):
   if not form.validate():
      return form.errors
   # TODO: Work this into the WTF validators.
   for k in keys:
      if form[k].data not in store:
         return 'Unknown key: {0}.'.format(form[k].data)
   return None

"""
Records a new course with given short (course code) and long (full description) names.
"""
def add_course(short, long, store):
   c = model.Course(short, long)
   c.add(store)
   return Response(dumps({
      'new': {
         'shortname': c.short,
         'longname': c.long
      }
   }))

"""
Records a new assignment in 'store' for with given 'title', returning a JSON object
of a single key 'new' containing fields for the new entry. Uses 'course' store key
as the parent for the new assignment.
"""
def add_assignment(courseKey, title, store):
   a = model.Assignment(title)
   a.add(a, store.getAgnostic(courseKey)(), store)
   return Response(dumps({
      'new': {
         'name': a.title,
         'questions': a.questions,
         'revision': a.key()
      }
   }))

"""
Records new questions in 'store' for with given 'prompts', returning a JSON object
of a single key 'new' containing fields for the new entry. Uses 'assignmentKey' store
key as the parent for the new assignment.
"""
def add_questions(assignmentKey, prompts, store):
   assignment = store.getAgnostic(assignmentKey)()
   newQs = []
   for p in prompts:
      q = model.Question(p)
      q.add(assignment, store)
      newQs.append(q)
   return Response(dumps({
      'new': map(lambda q : { 'revision': q.key(), 'prompt': q.prompt }, newQs)
   }))

"""
Removes the entry from its parent list, retaining the hash in the store as an archive.
"""
def remove(key, store):
   entry = store.getAgnostic(key)()
   entry.remove(store)
   return Response(dumps({ 'new': '' }))

"""
Records a new 'hashValue' for the field under 'hashKey' in the hash referenced by
'storeKey' in store.
"""
def revise(storeKey, hashKey, hashValue, store):
   entry = store.getAgnostic(storeKey)()
   entry[hashKey] = hashValue
   entry.revise(store)
   return Response(dumps({ 'new': str(hashValue) }))
