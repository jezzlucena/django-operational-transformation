import logging
import json
import traceback

from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from app.models import Conversation
from app.models import Mutation
from op_trans.redis_cli import RedisCli


def reset(request):
    Mutation.objects.all().delete()
    Conversation.objects.all().delete()
    return JsonResponse({
        "ok": True,
        "msg": "Database cleaned up of all Conversations and Mutations",
    })


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
            "url": "https://op-trans.herokuapp.com/"
        },
        "language": "python",
        "sources": "https://github.com/jezzlucena/django-operational-transformation",
        "answers": {
            "1": "I approached this challenge in 4 phases, in the following order of priority:\n\n\t1) Study the Operational Transformation algorithm so I can make informed architectural decisions;\n\t2) Set up a robust RESTful API using Django, Python, and PostgreSQL, along with a GitHub repository and a Heroku app that ;\n    3) Implement a (very) simple front-end app in the same Django project, using Bootstrap, Font Awesome, jQuery, CSS3, ES6, among some other tools. (by the way, I feel like this was my most hacky / least polished stab at this challenge - my most sincere apologies);\n\t4) Write up the very post-mortem testimonials you are reading right now.",
            "2": "If I had more time to work on this coding challenge, I would first solve the last mutation conflict resolution issues that I haven't been able to tackle; and second I would boost up the front end with a proper UI framerowk like Vue or React, plus a standardized design library like Google's Material Design (albeit this part would require some extra work on ensuring static files are properly served on AWS or a similar service - heroku is not the best at accomplishing this task).",
            "3": "This is complicated question to answer, but here I go:\nMy first instinct is to say that the time estimated to complete this task (6h) is not sufficient to deliver a code-complete solution that includes a concise architecture and build stack - I would estimate this task as a 16-to-20h job to reach production-level robustness.\nThat said, I have recognize that one of the most interesting parts of hiring is understanding how an engineer handles work under high-pressure circumstances, tight deadlines, and in that sense I believe there was just enough time. Maybe instead of extending the deadline, I would offer some extra boilerplate resources to ease out the engineer's issues with technicalities (e.g. setting up hosting services, dealing with CORS, ). When I have the opportunity to do recruiting, this has proven to be a great way to see through time and technical constraints - enabling me to take a closer look at the engineer's problem-solving approach and architectural/design abilities. Finally, I would say this suggestion is very dependent on role, team size, and stack."
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


def _trigger_mutation_event(mutation):
    conversation_id = mutation.conversation.identifier
    channel = 'sub:cnv:{}:mutation_event'.format(conversation_id)
    redis_cli = RedisCli.get()
    redis_cli.publish(channel, json.dumps({
        "eventType": "mutation",
        "mutationId": mutation.id,
        "conversationId": conversation_id,
        "text": mutation.conversation.text
    }).encode("utf-8"))


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
@transaction.atomic
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

            last_mutation = Mutation.objects.filter(
                conversation=conversation).last()
            if last_mutation is not None:
                if origin == last_mutation.origin:
                    mutation.origin = origin
                    mutation = _operational_transfrosmation(last_mutation, mutation)
                else:
                    conflict_mutation = Mutation.objects.filter(
                        conversation=conversation,
                        origin__contains=origin).first()

                    if conflict_mutation is not None:
                        conflict_candidates = Mutation.objects.filter(
                            conversation=conversation,
                            id__gt=conflict_mutation.id)
                        all_conflicts = [conflict_mutation] + list(conflict_candidates)

                        for old_mutation in all_conflicts:
                            mutation = _operational_transfrosmation(old_mutation, mutation)
            elif not all(v == 0 for v in origin.values()):
                return JsonResponse({
                    "ok": False,
                    "msg": "Origin outside conversation boundaries",
                }, status=201)

            new_text = _apply_mutation(mutation, conversation.text)
            conversation.text = new_text

            mutation.save()
            conversation.save()

            _trigger_mutation_event(mutation)

            return JsonResponse({
                "ok": True,
                "text": conversation.text,
            }, status=201)
        except Exception as err:
            error_msg = err.args[0] if err.args else "Unknown error"
            logging.exception(error_msg)
            return JsonResponse({
                "msg": error_msg,
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
                    "id": last_mutation.id,
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
            conversation_id = json.loads(request.body).get("conversationId")
            Conversation.objects.filter(identifier=conversation_id).delete()
        except Exception as err:
            error_msg = "Conversation not found"
            logging.exception(error_msg)
            return JsonResponse({
                "msg": error_msg,
                "ok": False,
            }, status=200)

        return JsonResponse({
            "ok": True,
        })

    return HttpResponseNotAllowed(['GET', 'DELETE'])

