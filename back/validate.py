ASST_FORM {
   REQUIRED: ['title']
   OPTIONAL: ['questions', 'id', 'parent', 'assigned']
}

def validateAssignmentForm(form):
   form = dict(form)
   for key in ASST_FORM.REQUIRED:
      if key not in form:
         raise ValueError('Missing form parameter (%s)' % key)

   
   

def accessLegal(entry, username, type='read'):
   return False

def tryJSONParse(s):
   try:
      return loads(s)
   except:
      raise ValueError('Illegal JSON')
