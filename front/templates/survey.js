{
   "survey": {
      "name": "{{ name }}",
      "questions": [
      {% for q in questions %}
         {
            "id": "{{ q.id }}",
            "prompt": "{{ q.prompt }}"
         }
      {% endfor %}
      ]
   }
}
