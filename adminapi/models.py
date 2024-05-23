from django.db import models
import uuid


class BaseModel(models.Model):
    """Abstract base model with common fields for other models."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class AdminAuth(BaseModel):
    """Model representing user authentication information."""
    ADMIN_ROLES= (
        ("SuperAdmin", "SuperAdmin"),
        ("Manager", "Manager")
    )
    f_name = models.CharField(max_length=20, blank=True, null=True)
    l_name = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    otp = models.PositiveIntegerField(default=0, blank=True, null=True)
    otp_status = models.BooleanField(default=False)
    otp_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    profile = models.ImageField(upload_to='admin/ProfileImage/', default="admin/ProfileImage/dummy.png")
    role = models.CharField(max_length=50, choices=ADMIN_ROLES, default= "Manager")

    def __str__(self):
        return self.email


class AdminWhitelistToken(BaseModel):
    """Model representing whitelist tokens for user authentication."""
    admin_id = models.ForeignKey(AdminAuth, on_delete=models.CASCADE, blank=True, null=True)
    token = models.TextField()



