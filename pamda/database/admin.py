from django.contrib import admin

from database.models import Deck, LearningSession, Progress, StageAssignment, Vocabulary

# Register your models here.
admin.site.register(Deck)
admin.site.register(Vocabulary)
admin.site.register(LearningSession)
admin.site.register(StageAssignment)
admin.site.register(Progress)