from django.contrib import admin

# Register your models here.
from posts import models

admin.site.register(models.Post)
admin.site.register(models.PostLike)
admin.site.register(models.PostComment)
admin.site.register(models.PostRating)
admin.site.register(models.BlacklistPost)
admin.site.register(models.PostView)
admin.site.register(models.PostMaterial)
admin.site.register(models.PostSave)
admin.site.register(models.CommentRating)
admin.site.register(models.PostImpressions)
