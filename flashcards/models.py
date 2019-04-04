import datetime

from django.contrib.auth.models import User
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

class LevelUser(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topscore = models.PositiveSmallIntegerField()
    topscore_perc_m = models.FloatField(blank=True,
                                        null=True,
                                        default=0)
    
    def award(self):
        potential_score = QuestionAnswer.objects.filter(level=self.level).count()
        if self.topscore == potential_score:
            return "🥇"
        elif self.topscore/potential_score >= .8:
            return "🥈"
        elif self.topscore/potential_score >= .5:
            return "🥉"
        else:
            return ""
    
    def __str__(self):
        return str(self.user) + "'s top score on " + str(self.level) + " is " + str(self.topscore)
