import json

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

db = {
    "conversations": {},
    "all_mutations": []
}

@csrf_exempt
def ping(request):
    return JsonResponse({
        "ok": True,
        "msg": "pong",
    })


@csrf_exempt
def info(request):
    return JsonResponse({
        "ok": True,
        "author": {
            "email": "jezzlucena@gmail.com",
            "name": "Jezz Lucena"
        },
        "frontend": {
            "url": "https://op-trans.herokuapp.com"
        },
        "language": "python",
        "sources": "https://github.com/jezzlucena/django-operational-transformation",
        "answers": {
            "1": "",
            "2": "",
            "3": ""
        }
    })


@csrf_exempt
def mutations(request):
    if request.method == 'POST':
        # try:
            parsed_data = json.loads(request.body)
            conversation_id = parsed_data.get("conversationId")
            author = parsed_data.get("author")
            data = parsed_data.get("data")
            origin = parsed_data.get("origin")

            if conversation_id not in db["conversations"].keys():
                db["conversations"][conversation_id] = {
                    "text": "",
                    "last_mutation": None,
                }

            conversation = db["conversations"].get(conversation_id)
            last_mutation = conversation.get("last_mutation")
            text = conversation.get("text")

            if last_mutation is not None:
                # TODO: Case where no transformation is necessary
                # EXTRAPOLATE TO N AUTHORS BY SETTING TO 0 BY DEFAULT
                if last_mutation["origin"].get("alice") == origin.get("alice") and \
                    last_mutation["origin"].get("bob") == origin.get("bob"):
                    # TODO: Transformation with same origin
                    print("TRANSFORMATION v1")
                else:
                    # TODO: Transformation with different origin
                    print("TRANSFORMATION v2")
                    raise Exception
            
            mutation = {
                "author": author,
                "data": {
                    "index": data.get("index"),
                    "length": data.get("length", None),
                    "text": data.get("text", None),
                    "type": data.get("type")
                },
                "origin": {
                    "alice": origin.get("alice"),
                    "bob": origin.get("bob"),
                },
            }

            if data.get("type") == "insert":
                # Check if last character inserted or next character to be inserted is a space
                # Then add a space if necessary
                if len(text) > 0 and not bool(set([text[-1], data["text"][0]]) & set([" ", "."])):
                    text = text + " "
                conversation["text"] = text + data["text"]
            elif data.get("type") == "delete":
                index = int(mutation["data"]["index"])
                length = int(mutation["data"]["length"])
                conversation["text"] = text[:index] + text[index+length:]
            else:
                raise Exception

            conversation["last_mutation"] = mutation

            return JsonResponse({
                "ok": True,
                "text": conversation["text"],
            }, status=201)
        # except:
        #     return JsonResponse({
        #         "msg": "Malformed request, please check and try again", 
        #         "ok": False,
        #         "text": "string, the current text of the conversation, after applying the mutation",
        #     }, status=400)

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def conversations(request):
    if request.method == 'GET':
        return JsonResponse({
            "conversations": conversations,
            "ok": False,
            "msg": "string, the current text of the conversation, after applying the mutation",
        })
    elif request.method == 'DELETE':
        try:
            db["conversations"].pop(request.DELETE.get("conversation_id"))
        except:
            return JsonResponse({
                "msg": "conversation not found", 
                "ok": False,
            }, status=404)
        return JsonResponse({
            "msg": "string, an error message, if needed", 
            "ok": False,
        })
    
    return HttpResponseNotAllowed(['GET', 'DELETE'])

