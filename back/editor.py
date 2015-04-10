from werkzeug.wrappers import Request, Response
from json import dumps
import model

def validate_form(form, store, keys):
   if not form.validate():
      return form.errors
   # TODO: Work this into the WTF validators.
   for k in keys:
      if form[k].data not in store:
         return 'Unknown parent key.'
   return None

"""
TODO
"""
def add_course(self, request):
   return Response(dumps({
      'new': {}
   }))

"""
Records a new assignment in 'store' for with given 'title', returning a JSON object
of a single key 'new' containing fields for the new entry. Uses 'course' store key
as the parent for the new assignment.
"""
def add_assignment(courseKey, title, store):
   a = model.Assignment(title)
   store.addAssignment(a, store.getAgnostic(courseKey)())
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
      store.addQuestion(q, assignment)
      newQs.append(q)
   return Response(dumps({
      'new': map(lambda q : { 'revision': q.key(), 'prompt': q.prompt }, newQs)
   }))

"""
TODO
"""
def remove(store):
   return Response('yeah, you betcha')

"""
Records a new 'hashValue' for the field under 'hashKey' in the hash referenced by
'storeKey' in store.
"""
def revise(storeKey, hashKey, hashValue, store):
   entry = store.getAgnostic(storeKey)()
   entry[hashKey] = hashValue
   store.reviseEntry(entry)
   return Response(dumps({ 'new': str(hashValue) }))
