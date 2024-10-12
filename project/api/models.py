from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=10, null=True)
    middle_name = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, null=True)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, null=True)
    dob = models.DateField(null=True, blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)
    otp_verified = models.BooleanField(default=False)

    # Adding custom related_name to avoid clashes
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'contact_number', 'email', 'dob']

    def __str__(self):
        return self.username

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)  # Set default value to False
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)