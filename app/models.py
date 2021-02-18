import json

from django.db import models
from django.utils.translation import gettext_lazy as _

class AuthorEnum(models.TextChoices):
    BOB = 'bob', _('bob')
    ALICE = 'alice', _('alice')


class BaseModel(models.Model):

    class Meta:
        abstract = True
        app_label = 'op_trans'


class Conversation(BaseModel):
    identifier = models.CharField(max_length=27, unique=True)
    text = models.TextField(default="")

    class Meta:
        abstract = False

    def __str__(self):
        return "%s %s" % (self.identifier, self.text)


class Mutation(BaseModel):
    author = models.CharField(max_length=5, choices=AuthorEnum.choices, default=AuthorEnum.BOB)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE)
    data = models.JSONField()
    origin = models.JSONField()

    class Meta:
        abstract = False

    def __str__(self):
        return "author: %s, origin: %s" % (self.author, json.dumps(self.origin))