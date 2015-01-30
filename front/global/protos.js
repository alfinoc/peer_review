window.PROTO = {};

window.PROTO.getQuestionProto = function(id, parent, prompt, answers) {
   prompt = prompt || 'New Prompt';
   answers = answers || [];
   var res = {
      type: 'question',
      hash: {
         prompt: prompt,
         answers: answers
      }
   };
   if (id) res['id'] = id;
   return res;
};

window.PROTO.getAssignmentProto = function(id, parent, title, questions) {
   title = title || 'Untitled';
   questions = questions || [];
   var res = {
      type: 'assignment',
      hash: {
         title: title,
         questions: questions
      }
   };
   if (id) res['id'] = id;
   return res;
};
