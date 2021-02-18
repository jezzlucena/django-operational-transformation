from django.contrib import admin

from app.models import Conversation
from app.models import Mutation

admin.site.register(Conversation)
admin.site.register(Mutation)