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


def _apply_mutation(mutation, text):
    data = mutation.data
    index = int(data["index"])
    if data.get("type") == "insert" and len(text) >= index:
        return text[:index] + data["text"] + text[index:]
    elif data.get("type") == "delete" and len(text) >= index + data.get("length"):
        length = int(data["length"])
        return text[:index] + text[index+length:]
    else:
        raise Exception("Invalid mutation: missing or invalid type / index / length combination")


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
        elif new_mutation.data["index"] >= last_index + last_length:
            new_mutation.data["index"] -= last_length
    
    return new_mutation


@csrf_exempt
def mutations(request):
    if request.method == 'POST':
        try:
            parsed_data = json.loads(request.body)
            conversation_id = parsed_data.get("conversationId", None)
            author = parsed_data.get("author")
            data = parsed_data.get("data")
            origin = parsed_data.get("origin")

            if not conversation_id:
                raise Exception("invalid conversation ID")

            conversation, _ = Conversation.objects.get_or_create(identifier=conversation_id)
            
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

            conflicting_mutation = Mutation.objects.filter(
                conversation=conversation,
                origin__contains=origin).first()

            if conflicting_mutation is not None:
                subsequent_mutations = Mutation.objects.filter(
                    conversation=conversation,
                    id__gt=conflicting_mutation.id)
                all_conflicts = [conflicting_mutation] + list(subsequent_mutations)

                for old_mutation in all_conflicts:
                    if old_mutation.origin != mutation.origin:
                        raise Exception("Broken mutation stack")
                    mutation = _operational_transfrosmation(old_mutation, mutation)
            
            new_text = _apply_mutation(mutation, conversation.text)
            conversation.text = new_text

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
            }, status=400)

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
                } if last_mutation else None,
            } for c in conversations]
        return JsonResponse({
            "conversations": results,
            "ok": True,
        })
    elif request.method == 'DELETE':
        try:
            Conversation.objects.get(identifier=request.DELETE.get("conversationId"))
        except Exception as err:
            print(traceback.format_exc())
            return JsonResponse({
                "msg": "Conversation not found", 
                "ok": False,
            }, status=400)
        
        return JsonResponse({
            "ok": True,
        })
    
    return HttpResponseNotAllowed(['GET', 'DELETE'])

