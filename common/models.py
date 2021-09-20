from django.db import models


# Create your models here.


class BaseModel(models.Model):
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AppName(models.Model):
    PRODUCTION = 'PRODUCTION'
    DEVELOPMENT = 'DEVELOPMENT'
    name_type_choices = (
        (DEVELOPMENT, 'DEVELOPMENT'),
        (PRODUCTION, 'PRODUCTION'),
    )
    host_name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=name_type_choices, default=DEVELOPMENT, unique=True)

    def __str__(self):
        return self.host_name
