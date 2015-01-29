import model
from json import loads

Q_PROTO = {
   'type': 'question',
   'suffix': model.Question.typeSuffix,
   'hashKeys': model.Question()._serializable
}

A_PROTO = {
   'type': 'assignment',
   'suffix': model.Assignment.typeSuffix,
   'hashKeys': model.Question()._serializable
}

R_PROTO = {
   'type': 'assignment',
   'suffix': model.Answer.typeSuffix,
   'hashKeys': model.Answer()._serializable
}

def _valuePair(actual, expected):
   return '(actual=%s,expected=%s)' % (actual, expected)

def _validateProto(actual, proto):
   # Check type.
   if actual['type'] != proto['type']:
      raise ValueError('Illegal proto type ' + valuePair(actual['type'], proto['type']))
   # Requisit store keys.
   for key in proto.hashKeys:
      if (not key in proto):
         raise ValueError('Missing proto key (%s)' % key)

def validateQuestionProto(actual):
   _validateProto(actual, R_PROTO)

def validateQuestionProto(actual):
   _validateProto(actual, Q_PROTO)

def validateAssignmentProto(actual):
   _validateProto(actual, A_PROTO)
   for q in actual.quesitons:
      validateQuestionProto(q)

def accessLegal(entry, username, type='read'):
   return False

def tryJSONParse(s):
   try:
      return loads(s)
   except:
      raise ValueError('Illegal JSON')
