from django.contrib import admin

from stories import models

# Register your models here.
admin.site.register(models.Story)
admin.site.register(models.StoryView)
admin.site.register(models.StoryRating)
