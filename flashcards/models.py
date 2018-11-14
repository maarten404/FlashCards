import datetime

from django.db import models

class Level(models.Model):
    """ A level is a set of questions (+answers) """
    name = models.CharField(max_length=200)

    def __str__(self):
        representation = self.name
        return representation

class QuestionAnswer(models.Model):
    """This will be the cue shown to the user"""
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        representation = str(self.question) + ": " + self.answer
        return representation