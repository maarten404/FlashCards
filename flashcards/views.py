import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .models import QuestionAnswer, Level

def index(request):
    return render(request, 'flashcards/index.html')

def select_level(request):
    # if next_page is not given, default to quiz
    if request.method == 'POST':
        next_page = request.POST.get("next_page")
    else:
        next_page = "quiz"

    levels = Level.objects.all()

    context = {'levels': levels,
               'next_page': next_page,
               }

    return render(request, 'flashcards/select_level.html', context)

def quiz(request, level_id):
    level = get_object_or_404(Level,id=level_id)

    # we get the question_nr from the session, will update it in this function
    # when necessary and write it back to the session in the end

    if "current_question_nr" in request.session:
        current_question_nr = request.session.get("current_question_nr")
        first_try = "True"
    else:
        current_question_nr = 0
        request.session["current_question_nr"] = 0
        request.session["score"] = 0
        first_try = "True"
    
    # if we received an answer, we will check whether it is correct and if so
    # whether it was a first try. 
    # If it is correct, we go to the next question. If it was the first try,
    # the score is increased by one.
    if "answer" in request.POST:
        if(str.lower(request.POST.get("answer")) == 
            QuestionAnswer.objects.get(id=request.POST.get("question_id")).answer):
            if request.POST.get("first_try") == "True":
                request.session["score"] += 1
            current_question_nr += 1
            first_try = "True"
        else:
            first_try = "False"


    # If all questions are done, we go to the end template showing the score
    # we also remove current_question_nr and score from the session so that
    # next round we start with a clean slate
    # to do: make django do the length in the query
    if(current_question_nr >= 
        len(QuestionAnswer.objects.filter(level_id=level_id))):
        context = {'current_question_nr': current_question_nr,
                   'score': request.session["score"],}
        del request.session["current_question_nr"]
        del request.session["score"]
        return render(request, 'flashcards/end.html', context)

    request.session["current_question_nr"] = current_question_nr

    context = {'current_question': 
        QuestionAnswer.objects.filter(level_id=level_id).order_by('id')[current_question_nr],
               'score': request.session["score"],
               'current_question_nr': current_question_nr,
               'first_try': first_try,
               'level_id': level_id,
               }
    return render(request, 'flashcards/quiz.html', context)

@login_required
def edit(request,level_id):
    level = get_object_or_404(Level,id=level_id)

    if request.method != 'POST':
        text_rep = ""
        for question_answer in(QuestionAnswer.objects.filter(level_id=level_id).order_by('id')):
            text_rep += question_answer.question + ","
            text_rep += question_answer.answer + "\r\n"

        context = {'text_rep': text_rep,
                   'level': level,
                   #'level_id': level_id
                  }
        return render(request, 'flashcards/edit.html', context)
    else:
        QuestionAnswer.objects.filter(level_id=level_id).delete()

        current_question_nr = 0
        request.session["current_question_nr"] = 0
        request.session["score"] = 0
        first_try = "True"

        try:
            shuffle = request.POST.get("shuffle")
            text_rep = request.POST.get("text_rep").split("\r\n")
        except ValueError:
            return HttpResponseBadRequest()

        if shuffle == "shuffle":
            random.shuffle(text_rep)

        for line in text_rep:
            question_answer = line.split(",")
            if len(question_answer) == 2:
                new_questionanswer = QuestionAnswer()
                new_questionanswer.question = question_answer[0]
                new_questionanswer.answer = question_answer[1]
                new_questionanswer.level = level
                new_questionanswer.save()
            else:
                next

        return HttpResponseRedirect(reverse('flashcards:index'))
