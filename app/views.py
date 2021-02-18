import json
import traceback

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Conversation
from app.models import Mutation

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
    last_data = last_mutation.data
    data = current_mutation.data

    # Make a copy of all values in the current mutation to avoid changing
    # important data in the conversation database 
    new_mutation = Mutation(
        author=current_mutation.author,
        conversation=current_mutation.conversation,
        data=current_mutation.data.copy(),
        origin=current_mutation.origin.copy())

    new_mutation.origin[last_mutation.author] += 1

    # If last mutation was an insertion and current mutation's index
    # is greater than or equals last mutation's index, increment
    # the new mutation's index
    if last_data["type"] == "insert" and data["index"] >= last_data["index"]:
        new_mutation.data["index"] += len(last_data["text"])
    
    # Otherwise, if last mutation was a deletion
    elif last_data["type"] == "delete":
        last_index = last_data["index"]
        last_length = last_data["length"]

        # - If the new mutation is being attempted amidst the deleted characters;
        #   then set the new index to last mutation's index
        if data["index"] >= last_index and data["index"] < last_index + last_length:
            new_mutation.data["index"] = last_index

        # Otherwise if the new mutation is being attempted at a greater index
        # than last deletion index+length;
        # then Subtract last mutation's length from the new index 
        elif new_mutation.data["index"] > last_index + last_length:
            new_mutation.data["index"] -= len(last_data["text"])
    
    return new_mutation


@csrf_exempt
def mutations(request):
    if request.method == 'POST':
        try:
            parsed_data = json.loads(request.body)
            print("TESTING PARSING OF BODY")
            print(request.body)
            print(parsed_data)
            print(parsed_data.get("conversationId"))
            print("TESTING PARSING OF BODY")
            conversation_id = parsed_data.get("conversationId")
            author = parsed_data.get("author")
            data = parsed_data.get("data")
            origin = parsed_data.get("origin")

            conversation, _ = Conversation.objects.get_or_create(identifier=conversation_id)
            last_mutation = Mutation.objects.filter(conversation=conversation).last()
            text = conversation.text
            
            data_length = data.get("length", None)
            data_text = data.get("text", None)
            mutation = Mutation(
                author=author,
                conversation=conversation,
                data={
                    "index": int(data.get("index")),
                    "type": data.get("type")
                },
                origin={
                    "alice": int(origin.get("alice")),
                    "bob": int(origin.get("bob")),
                })

            if data_length is not None:
                mutation.data["length"] = data_length

            if data_text is not None:
                mutation.data["text"] = data_text

            print(author,
                data.get("type")+"s",
                "\""+str(data.get("text") if data["type"] == "insert" else data.get("length"))+"\"",
                "at",
                data.get("index"))

            is_invalid_mutation = False
            if last_mutation is not None:
                last_author = last_mutation.author
                if last_mutation.origin == mutation.origin and last_author != author:
                    mutation = _operational_transfrosmation(last_mutation, mutation)
                else:
                    last_origin = last_mutation.origin

                    # Check if all author indices remain the same in the new origin,
                    # except for the last author's index
                    for key in mutation.origin.keys():
                        if key != last_author and origin.get(key) != last_origin.get(key):
                            is_invalid_mutation = True
                    
                    # Check if current author's index equals last mutation's author
                    # index incremented by 1, meaning no transformation is necessary
                    if last_origin[last_author]+1 != origin[last_author]:
                        is_invalid_mutation = True
            else:
                for key in origin.keys():
                    if origin[key] != 0:
                        is_invalid_mutation = True

            if is_invalid_mutation:
                raise Exception("Invalid mutation: wrong origin for this conversation")

            index = int(mutation.data["index"])
            if data.get("type") == "insert" and len(text) >= data.get("index"):
                conversation.text = text[:index] + mutation.data["text"] + text[index:]
            elif data.get("type") == "delete" and len(text) >= data.get("index")+data.get("length"):
                length = int(mutation.data["length"])
                conversation.text = text[:index] + text[index+length:]
            else:
                raise Exception("Invalid mutation: missing or invalid type / index / length combination")

            mutation.save()
            conversation.save()

            return JsonResponse({
                "ok": True,
                "text": conversation.text,
            }, status=201)
        except Exception as err:
            print(traceback.format_exc())
            return JsonResponse({
                "msg": err.args[0] if err.args else "Unknown error",
                "ok": False,
            }, status=201)

    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def conversations(request):
    if request.method == 'GET':
        conversations = Conversation.objects.all()
        results = []
        for c in conversations:
            last_mutation = Mutation.objects.filter(conversation=c).last()
            results = [{
                "id": c.identifier,
                "text": c.text,
                "lastMutation": {
                    "author": last_mutation.author,
                    "data": last_mutation.data,
                    "origin": last_mutation.origin,
                },
            } for c in conversations]
        return JsonResponse({
            "conversations": results,
            "ok": True,
        })
    elif request.method == 'DELETE':
        try:
            Conversation.objects.get(identifier=request.DELETE.get("conversation_id"))
        except Exception as err:
            print(traceback.format_exc())
            return JsonResponse({
                "msg": "Conversation not found", 
                "ok": False,
            }, status=404)
        
        return JsonResponse({
            "ok": True,
        })
    
    return HttpResponseNotAllowed(['GET', 'DELETE'])

