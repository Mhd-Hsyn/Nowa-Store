import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class User(BaseModel):
    fname = models.CharField(max_length=255, blank=True, null=True)
    lname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255,unique=True)
    password = models.TextField()
    contact = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    profile = models.ImageField(upload_to="User/", default="User/dummy.png")
    otp = models.IntegerField(default=0)
    otp_count = models.IntegerField(default=0)
    otp_status = models.BooleanField(default=False)
    no_of_attempts_allowed = models.IntegerField(default=3)
    no_of_wrong_attempts = models.IntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.email}"

class UserWhitelistToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

