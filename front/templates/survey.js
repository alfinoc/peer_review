if (window.EXTERNS == undefined) {
   window.EXTERNS = {};
}

window.EXTERNS.getSurvey = function() {
   return {
      "name": "{{ name }}",
      "course": {
         "id": "{{ course.id }}",
         "name": "{{ course.name }}"
      },
      "questions": [
      {% for q in questions %}
         {
            "id": "{{ q.id }}",
            "prompt": "{{ q.prompt }}"
         }
      {% endfor %}
      ]
   };
}
