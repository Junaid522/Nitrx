from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from common.models import BaseModel


# Create your models here.


class User(AbstractUser, BaseModel):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    GENDER_TYPE = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    )
    profile_qr = models.FileField(upload_to='static/user_qr_codes/', blank=True, null=True)
    image = models.FileField(upload_to='static/profile_image/', null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_TYPE, default=OTHER)
    phone_number = PhoneNumberField(null=True, blank=True)
    age = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    verified_account = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    search_privacy = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    otp_enabled = models.BooleanField(default=False)
    image_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class AccountInformation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = CountryField()
    site_visit = models.BooleanField(default=False)
    partner_info = models.BooleanField(default=False)
    search_privacy = models.BooleanField(default=False)
    store_contacts = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class WebsiteVerification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class FollowUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_user')

    def __str__(self):
        return self.user.username


class ReportUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_user')

    def __str__(self):
        return self.user.username


class BlockUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_user')

    def __str__(self):
        return self.user.username


class Otp(BaseModel):
    EMAIL = 'EMAIL'
    NUMBER = 'NUMBER'
    LOGIN = 'LOGIN'
    VERIFY = 'VERIFY'
    OTP_CHOICES = (
        (EMAIL, 'EMAIL'),
        (NUMBER, 'NUMBER'),
    )
    OTP_FOR_CHOICES = (
        (VERIFY, 'VERIFY'),
        (LOGIN, 'LOGIN'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    otp_type = models.CharField(max_length=255, choices=OTP_CHOICES, default=EMAIL)
    otp_for = models.CharField(max_length=255, choices=OTP_FOR_CHOICES, default=VERIFY)
