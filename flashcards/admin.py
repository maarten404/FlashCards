from django.contrib import admin

from flashcards.models import QuestionAnswer, Level, LevelUser

admin.site.register(QuestionAnswer)
admin.site.register(Level)
admin.site.register(LevelUser)
