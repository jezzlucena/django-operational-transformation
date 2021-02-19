import json

from django.shortcuts import render

@csrf_exempt
def index(request):
    return render(
        request, "index.html", request_data)