from django.urls import path

from . import views

app_name = 'flashcards'

urlpatterns = [
    path('', views.index, name='index'),
    path('edit', views.edit_flashcards, name='edit'),
    path('quiz', views.quiz, name='quiz'),
]
