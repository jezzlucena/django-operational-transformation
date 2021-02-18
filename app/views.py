import json

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

local_db = {
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


def _operational_transfrosmation(last_mutation, current_mutation):
    last_author = last_mutation["author"]
    last_origin = last_mutation["origin"]
    last_data = last_mutation["data"]

    author = current_mutation["author"]
    origin = current_mutation["origin"]
    data = current_mutation["data"]

    # Check if all author indices remain the same in the new origin,
    # except for the last author's index
    for key in origin.keys():
        if key != last_author and origin[key] != last_origin[key]:
            raise Exception("Error transforming mutation: invalid origin")
    
    # Check if current author's index equals last mutation's author
    # index incremented by 1, meaning no transformation is necessary
    if (last_origin[last_author]+1 == origin[last_author]):
        return current_mutation

    # Otherwise, if both mutations have the same origin,
    # a transformation is necessary
    elif last_origin == origin:

        # Make a copy of all values in the current mutation to avoid changing
        # important data in the conversation database 
        new_mutation = {
            "author": author,
            "data": data.copy(),
            "origin": origin.copy(),
        }

        new_mutation["origin"][last_author] += 1

        # If last mutation was an insertion and current mutation's index
        # is greater than or equals last mutation's index, increment
        # the new mutation's index
        if last_data.get("type") == "insert" and data.get("index") >= last_data.get("index"):
            new_mutation["data"]["index"] += len(last_data["text"])
        
        # Otherwise, if last mutation was a deletion
        elif last_data.get("type") == "delete":
            last_index = last_data.get("index")
            last_length = last_data.get("length")

            # - If the new mutation is being attempted amidst the deleted characters;
            #   then set the new index to last mutation's index
            if data.get("index") >= last_index and data.get("index") < last_index + last_length:
                new_mutation["data"]["index"] = last_index

            # Otherwise if the new mutation is being attempted at a greater index
            # than last deletion index+length;
            # then Subtract last mutation's length from the new index 
            elif data.get("index") > last_index + last_length:
                new_mutation["data"]["index"] -= len(last_data["text"])
        
        return new_mutation
        
    # Otherwise, a transformation is not possible
    raise Exception("Error transforming mutation: invalid origin")


@csrf_exempt
def mutations(request):
    if request.method == 'POST':
        try:
            parsed_data = json.loads(request.body)
            conversation_id = parsed_data.get("conversationId")
            author = parsed_data.get("author")
            data = parsed_data.get("data")
            origin = parsed_data.get("origin")

            if conversation_id not in local_db["conversations"].keys():
                local_db["conversations"][conversation_id] = {
                    "text": "",
                    "last_mutation": None,
                }

            conversation = local_db["conversations"].get(conversation_id)
            last_mutation = conversation.get("last_mutation")
            text = conversation.get("text")
            
            data_length = data.get("length", None)
            data_text = data.get("text", None)
            mutation = {
                "author": author,
                "data": {
                    "index": int(data.get("index")),
                    "type": data.get("type")
                },
                "origin": {
                    "alice": int(origin.get("alice")),
                    "bob": int(origin.get("bob")),
                },
            }

            if data_length is not None:
                mutation["data"]["length"] = data_length

            if data_text is not None:
                mutation["data"]["text"] = data_text

            print(author,
                data.get("type")+"s",
                "\""+str(data.get("text") if data["type"] == "insert" else data.get("length"))+"\"",
                "at",
                data.get("index"))

            if last_mutation is not None:
                mutation = _operational_transfrosmation(last_mutation, mutation)
            else:
                for key in origin.keys():
                    if origin[key] != 0:
                        raise Exception("Invalid mutation, bad origin for given conversation")

            index = int(mutation["data"]["index"])
            if data.get("type") == "insert" and len(text) >= data.get("index"):
                conversation["text"] = text[:index] + mutation["data"]["text"] + text[index:]
            elif data.get("type") == "delete" and len(text) >= data.get("index")+data.get("length"):
                length = int(mutation["data"]["length"])
                conversation["text"] = text[:index] + text[index+length:]
            else:
                raise Exception("Invalid mutation type or index")

            conversation["last_mutation"] = mutation
            local_db["all_mutations"].append(mutation)

            return JsonResponse({
                "ok": True,
                "text": conversation["text"],
            }, status=201)
        except Exception as err:
            return JsonResponse({
                "msg": err.args[0] if err.args else "Unknown error",
                "ok": False,
                "text": text,
            }, status=400)

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def conversations(request):
    if request.method == 'GET':
        conversations = [{
            "id": c["last_mutation"],
            "lastMutation": c["last_mutation"],
            "lastMutation": c["last_mutation"],
        } for c in local_db["conversations"]]
        return JsonResponse({
            "conversations": conversations,
            "ok": True,
        })
    elif request.method == 'DELETE':
        try:
            local_db["conversations"].pop(request.DELETE.get("conversation_id"))
        except:
            return JsonResponse({
                "msg": "Conversation not found", 
                "ok": False,
            }, status=404)
        
        return JsonResponse({
            "ok": True,
        })
    
    return HttpResponseNotAllowed(['GET', 'DELETE'])

