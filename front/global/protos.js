window.PROTO = {};

window.PROTO.getQuestionProto = function(id, prompt, answers) {
   prompt = prompt || 'New Prompt';
   answers = answers || [];
   var res = {
      type: 'question',
      hash: {
         prompt: prompt,
         answers: []
      }
   };
   if (id) res['id'] = id;
   return res;
};

window.PROTO.getAssignmentProto = function(id, title, questions) {
   title = title || 'Untitled';
   questions = questions || [];
   var res = {
      type: 'question',
      hash: {
         title: title,
         questions: []
      }
   };
   if (id) res['id'] = id;
   return res;
};
