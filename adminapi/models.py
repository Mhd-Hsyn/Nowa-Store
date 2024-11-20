from django.db import models
import uuid
from django.core.exceptions import ValidationError


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

    def clean(self):
        if self.role == "SuperAdmin" and AdminAuth.objects.filter(role="SuperAdmin").exclude(id=self.id).exists():
            raise ValidationError("There can be only one SuperAdmin.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean is called before saving
        super(AdminAuth, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


class AdminWhitelistToken(BaseModel):
    """Model representing whitelist tokens for user authentication."""
    admin_id = models.ForeignKey(AdminAuth, on_delete=models.CASCADE, blank=True, null=True)
    token = models.TextField()



class ProductCategory(BaseModel):
    name= models.CharField(max_length=50, unique=True)
    image= models.ImageField(upload_to="product/product_category/", blank=True, null=True)
    banner_image= models.ImageField(upload_to="product/banner_image/", blank=True, null=True)
    banner_text= models.TextField(blank=True, null=True)
    is_banner=models.BooleanField(default=False)
    admin_id= models.ForeignKey(AdminAuth, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


class Brand(BaseModel):
    name= models.CharField(max_length=100, unique=True)
    text= models.TextField(blank=True, null=True)
    image= models.ImageField(upload_to="product/brand/")
    admin_id= models.ForeignKey(AdminAuth, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"


class Product(BaseModel):
    name= models.CharField(max_length=250, unique= True)
    brand= models.ForeignKey(Brand, on_delete=models.SET_NULL, related_name="brands_products", blank=True, null=True)
    category= models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, related_name="category_products", blank=True, null=True)
    stock= models.PositiveIntegerField()
    sold= models.PositiveIntegerField(default= 0)
    is_available= models.BooleanField(default=True)
    overview= models.TextField(blank=True, null=True)
    description= models.TextField(blank=True, null=True)
    specification= models.TextField(blank=True, null=True)
    price= models.PositiveIntegerField()
    discounted_price= models.PositiveIntegerField(blank=True, null=True)
    is_discount= models.BooleanField(default=False)
    discount_date_start= models.DateTimeField(blank=True, null=True)
    discount_date_end= models.DateTimeField(blank=True, null=True)
    delivery_info= models.TextField(blank=True, null=True)
    admin_id= models.ForeignKey(AdminAuth, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class ProductImage(models.Model):
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    image= models.ImageField(upload_to="product/product_images/")


