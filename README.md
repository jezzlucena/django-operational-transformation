# django-operational-transformation
A boilerplate Opperational Transformation implementation using Django, Bootstrap, and jQuery to provide interface

# Live Demo
https://op-trans.herokuapp.com/

# RESTful API

### GET /ping

Response:
```
200 {
  "ok": true,
  "msg": "pong"
}
```

### GET /info

Response:
```
200 {
  "ok": true,
  "author": {
    "email": "string",
    "name": "string"
  },
  "frontend": {
    "url": "string, the url of your frontend."
  },
  "language": "node.js | python",
  "sources": "string, the url of a github repository including your backend sources and your frontend sources",
  "answers": {
    "1": "string, answer to the question 1",
    "2": "string, answer to the question 2",
    "3": "string, answer to the question 3"
  }
}
```

### POST /mutations

Body:
```
{
  "author": "alice | bob",
  "conversationId": "string",
  "data": {
    "index": "number",
    "length": "number | undefined",
    "text": "string | undefined",
    "type": "insert | delete"
  },
  "origin": {
    "alice": "integer",
    "bob": "integer"
  }
}
```

Response:
```
201 {
  "msg": "an error message, if needed",
  "ok": "boolean",
  "text": "string, the current text of the conversation, after applying the mutation"
}
```

### GET /conversations

Response:
```
200 {
  "conversations": [
    {
      "id": "string",
      "lastMutation": "Object, The last mutation applyed on this conversation",
      "text": "string"
    },
    "..."
  ],
  "msg": "string, an error message, if needed",
  "ok": "boolean"
}
```

### DELETE /conversations

Response:
```
204 {
  "msg": "string, an error message, if needed",
  "ok": "boolean"
}
```

### GET /reset

Response:
```
200 {
  "ok": true,
  "msg": "pong"
}
```
