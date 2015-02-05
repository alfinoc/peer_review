from wtforms import Form, IntegerField, StringField, ValidationError, validators
from json import loads
import model

def jsonList(form, json):
   print form, json
   try:
      parsed = loads(json.data)
   except:
      raise ValidationError('Illegal JSON: ' + str(json.data))
   if type(parse) != list:
      raise ValidationError('JSON object must be a list.')

class EditAssignmentForm(Form):
   asst_id = IntegerField('Assignment ID')
   title = StringField('Assignment Title')
   questions = StringField('Question List', validators=[jsonList])

   def entry(self):
      id = self.asst_id.data
      title = self.title.data
      questions = loads(self.questions.data)
      return model.Assignment(id, title, questions)
