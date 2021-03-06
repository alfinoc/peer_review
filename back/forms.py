from wtforms import Form, IntegerField, StringField, ValidationError, validators
from json import loads
import model

LEGAL_EDITS = {
   'asst': ['title'],
   'quest': ['prompt'],
   'course': ['title'],
}

# Avoids error if the field does not contain a properly formatted json list.
# No constraints on list values.
def jsonList(form, json):
   try:
      parsed = loads(json.data)
   except:
      raise ValidationError('Illegal JSON: ' + str(json.data))
   if type(parsed) != list:
      raise ValidationError('JSON object must be a list.')

# Returns the suffix of the ':' delimited store key.
def suffix(storeKey):
   return storeKey.split(':')[1]

# Avoids error iff the store key has a legal suffix.
def validate_suffix(form, storeKey):
   legal = LEGAL_EDITS.keys()
   if ':' not in storeKey.data or suffix(storeKey.data) not in legal:
      raise ValidationError('suffix must be one of {0}.'.format(legal))

# Avoids error iff hashKey is a legal edit.
def editable(form, hashKey):
   validate_suffix(form, form.store_key)
   legal = LEGAL_EDITS[suffix(form.store_key.data)]
   if hashKey.data not in legal:
      raise ValidationError('must be one of {0}.'.format(legal))

# Avoids error iff field's data is not empty or all whitespace.
def non_empty(form, field):
   if field.data.strip() == '':
      raise ValidationError('must be non-empty')

class ChangeForm(Form):
   store_key = StringField('Persistent Key for Entry (suffix and ID)',
                           [validators.Required(), validate_suffix])
   hash_key = StringField('Entry Key', [validators.Required(), editable])
   hash_value = StringField('Entry Value', [validators.Required()])

class AddCourseForm(Form):
   short_name = StringField('Short title of the new course.', [validators.Required()])
   long_name = StringField('Long title of the new course.', [validators.Required()])

class AddAssignmentForm(Form):
   parent_key = StringField('Key of parent store entry (suffix and ID).',
                            [validators.Required()])
   title = StringField('Title of the new assignment.', default='')

class AddQuestionsForm(Form):
   parent_key = StringField('Key of parent store entry (suffix and ID).',
                            [validators.Required()])
   prompts = StringField('Title of the new assignment.', [jsonList])

class RemoveForm(Form):
   key = StringField('Key of store entry to remove.',
                     [validators.Required(), validate_suffix])
