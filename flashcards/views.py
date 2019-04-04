from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, reverse

from .helper import new_question_list
from .models import QuestionAnswer, Level, LevelUser

def index(request):
    return render(request, 'flashcards/index.html')

def about(request):
    return render(request, 'flashcards/about.html')

def select_level(request):
    # if next_page is not given, default to quiz
    if request.method == 'POST':
        next_page = request.POST.get("next_page")
    else:
        next_page = "quiz"

    levels = Level.objects.order_by(Lower('name'))

    awards = {}

    if request.user.is_authenticated:
        for level in LevelUser.objects.filter(user=request.user):
            awards[level.level.id] = level.award()

    if "question_list" in request.session:
        del request.session["question_list"]
    if "score" in request.session:
        del request.session["score"]
        
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
        question_list = new_question_list(level)
    else:
        question_list = request.session["question_list"]

        if question_list == []: # quiz is done
            score = request.session["score"]
            potential_score = QuestionAnswer.objects.filter(
                level=level).count()
            context = {'score': score,
                       'level': level,
                       'potential_score': potential_score,
                       'prev_question': prev_question,
                       'award': "",}
            if request.user.is_authenticated:
                try:
                    topscore = LevelUser.objects.get(
                        level_id=level_id,user=request.user).topscore
                except LevelUser.DoesNotExist:
                    topscore = 0

                if score >= topscore:
                    LevelUser.objects.filter(level_id=level_id, 
                                             user=request.user).delete()
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

    if current_question.level != level:
        print("Yeah this is not the correct level.")
        request.session["score"] = 0
        question_list = new_question_list(level)

    request.session["question_list"] = question_list
    
    context = {'current_question': current_question,
               'prev_question': prev_question,
               'score': request.session["score"],
               'level_id': level_id,
               }
    return render(request, 'flashcards/quiz.html', context)

def practice(request):
    # if there's an answer in the request, we check if it's correct, add 1 to
    # the score and give back the question and the answer.

    prev_question = {}
    if "answer" in request.POST:
        question = QuestionAnswer.objects.get(id=request.POST.get("question_id"))

        if(str.lower(request.POST.get("answer")) == question.answer):
            prev_question["correct"] = True
            if(request.session["nr_tries"] < settings.LENGTH_PRACTICE):
                request.session["score"] += 1
        else:
            prev_question["correct"] = False
        
        request.session["nr_tries"] += 1
        prev_question["question"] = question

    # if there is no question list in the session, we take ten random questions
    if "question_list" not in request.session:
        question_list = list(
        QuestionAnswer.objects.order_by('?').values_list('id',
            flat = True)[:settings.LENGTH_PRACTICE]
        )
        request.session["score"] = 0
        request.session["nr_tries"] = 0
    # if there is a question_list we are midpractice so we get the list
    else:
        question_list = request.session["question_list"]

    #if the previous question was wrong we put it back into the question list
    if prev_question.get("correct") == False:
        question_list.insert(0,request.POST.get("question_id"))

    # if the list is there and it is empty, the practice is done
    if question_list == []:
        award = ""
        if request.session["score"] == settings.LENGTH_PRACTICE:
            award = "🥇"

        context = {'score': request.session["score"],
                   'potential_score': settings.LENGTH_PRACTICE,
                   'prev_question': prev_question,
                   'award': award,}

        del request.session["question_list"]
        del request.session["score"]

        return render(request, 'flashcards/end.html', context)

    # the current question we get from the question_id list
    current_question = QuestionAnswer.objects.get(pk=question_list.pop())

    request.session["question_list"] = question_list
    

    context = {'current_question': current_question,
               'prev_question': prev_question,
               'score': request.session["score"],
               'question_list': question_list}

    return render(request, 'flashcards/practice.html', context)




@login_required
def edit(request,level_id):
    if level_id != 0:
        level = get_object_or_404(Level,id=level_id)
    else:
        level = Level()
        level.save()

    if request.method != 'POST':
        text_rep = ""
        for question_answer in(QuestionAnswer.objects.filter(level_id=level_id).order_by('id')):
            text_rep += question_answer.question + ","
            text_rep += question_answer.answer + "\r\n"

        context = {'text_rep': text_rep,
                   'level': level,
                  }
        return render(request, 'flashcards/edit.html', context)
    else:
        # We will update the name of the level and the related questions.
        try:
            name = request.POST.get("name")
        except ValueError:
            return HttpResponseBadRequest()
        level.name = name
        level.save()

        QuestionAnswer.objects.filter(level_id=level_id).delete()
        try:
            text_rep = request.POST.get("text_rep").split("\r\n")
        except ValueError:
            return HttpResponseBadRequest()

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

@login_required
def delete(request,level_id):
    level = get_object_or_404(Level,id=level_id)
    level.delete()
    
    return HttpResponseRedirect(reverse('flashcards:index'))