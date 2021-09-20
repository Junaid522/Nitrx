from django.contrib import admin

# Register your models here.
from categories import models

admin.site.register(models.Category)
admin.site.register(models.SelectedCategories)
