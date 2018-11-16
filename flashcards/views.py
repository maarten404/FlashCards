import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .models import QuestionAnswer, Level, LevelUser

def index(request):
    return render(request, 'flashcards/index.html')

def select_level(request):
    # if next_page is not given, default to quiz
    if request.method == 'POST':
        next_page = request.POST.get("next_page")
    else:
        next_page = "quiz"

    levels = Level.objects.all()

    awards = {}

    if request.user.is_authenticated:
        for level in LevelUser.objects.filter(user=request.user):
            awards[level.level.id] = level.award()
        
    context = {'levels': levels,
               'awards': awards,
               'next_page': next_page,
               }

    return render(request, 'flashcards/select_level.html', context)

def quiz(request, level_id):
    level = get_object_or_404(Level,id=level_id)

    # if there's an answer in the request, we check if it's correct, add 1 to
    # the score and give back the question and the answer.

    prev_question = {}
    if "answer" in request.POST:
        question = QuestionAnswer.objects.get(id=request.POST.get("question_id"))

        if(str.lower(request.POST.get("answer")) == question.answer):
            prev_question["correct"] = True
            request.session["score"] += 1
        else:
            prev_question["correct"] = False
        
        prev_question["question"] = question

    # we make a shuffled question_id list if there is none. If there is, we 
    # check if the list is empty because if so the quiz is done end we show
    # the end view and update the top score.

    if "question_list" not in request.session:
        # new quiz: fill question_list
        request.session["score"] = 0
        question_list = list(
            QuestionAnswer.objects.filter(level=level).values_list('id', flat = True)
            )
        random.shuffle(question_list)
    else:
        question_list = request.session["question_list"]

        if question_list == []: # quiz is done
            score = request.session["score"]
            potential_score = QuestionAnswer.objects.filter(level=level).count()
            context = {'score': score,
                       'potential_score': potential_score,
                       'prev_question': prev_question,
                       'award': "",}
            if request.user.is_authenticated:
                try:
                    topscore = LevelUser.objects.get(level_id=level_id,user=request.user).topscore
                except LevelUser.DoesNotExist:
                    topscore = 0

                if score >= topscore:
                    LevelUser.objects.filter(level_id=level_id, user=request.user).delete()
                    new_leveluser = LevelUser()
                    new_leveluser.level = Level.objects.get(pk=level_id)
                    new_leveluser.user = request.user
                    new_leveluser.topscore = score
                    new_leveluser.save()
                    context["award"] = new_leveluser.award()

            del request.session["question_list"]
            del request.session["score"]
            return render(request, 'flashcards/end.html', context)


    current_question = QuestionAnswer.objects.get(pk=question_list.pop())

    request.session["question_list"] = question_list
    
    context = {'current_question': current_question,
               'prev_question': prev_question,
               'score': request.session["score"],
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

        request.session["question_list"] = []
        request.session["score"] = 0

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
