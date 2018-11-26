# helper functions for views.py
import random

from .models import QuestionAnswer

def new_question_list(level):
    print("new_question_list for level:", level.id)
    question_list = list(
        QuestionAnswer.objects.filter(level=level).values_list('id', flat = True)
        )
    random.shuffle(question_list)
    return question_list