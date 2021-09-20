from django.contrib import admin

# Register your models here.
from chat_app.models import MessageModel, Thread

admin.site.register(MessageModel)
admin.site.register(Thread)
