from django.urls import path

from . import views

app_name = 'flashcards'

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/<int:level_id>/', views.edit, name='edit'),
    path('quiz/<int:level_id>/', views.quiz, name='quiz'),
    path('select_level', views.select_level, name='select_level'),
]
