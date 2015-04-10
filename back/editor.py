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

def add_course(self, request):
   return Response(dumps({
      'new': {}
   }))

def add_assignment(course, title, store):
   a = model.Assignment(title)
   store.addAssignment(a, store.getAgnostic(course)())
   return Response(dumps({
      'new': {
         'name': a.title,
         'questions': a.questions,
         'revision': a.key()
      }
   }))

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

def remove(self, request, store):
   return Response('yeah, you betcha')

def revise(storeKey, hashKey, hashValue, store):
   # Change hash_key's value and store the revision.
   entry = store.getAgnostic(storeKey)()
   entry[hashKey] = hashValue
   store.reviseEntry(entry)
   return Response(dumps({ 'new': str(hashValue) }))
