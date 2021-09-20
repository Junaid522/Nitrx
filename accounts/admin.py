from django.contrib import admin

# Register your models here.
from accounts import models

admin.site.register(models.User)
admin.site.register(models.FollowUser)
admin.site.register(models.ReportUser)
admin.site.register(models.BlockUser)
admin.site.register(models.AccountInformation)
admin.site.register(models.WebsiteVerification)
admin.site.register(models.Otp)
