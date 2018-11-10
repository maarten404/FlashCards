from django.db import models

class QuestionAnswer(models.Model):
    """This will be the cue shown to the user"""
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        representation = str(self.question) + ": " + self.answer
        return representation