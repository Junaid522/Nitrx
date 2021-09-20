from django.db import models

from accounts.models import User
from common.models import BaseModel


class Category(BaseModel):
    parent = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='static/categories_images', max_length=254)

    def __str__(self):
        return self.name


class SelectedCategories(BaseModel):
    categories = models.ManyToManyField(Category, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
