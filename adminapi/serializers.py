from uuid import UUID
from rest_framework import serializers
from .models import (
    AdminAuth,
    Brand,
    ProductCategory,
    Product
)
from passlib.hash import django_pbkdf2_sha256 as handler


class AdminRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuth
        fields = ["f_name", "l_name", "email", "password", "address", "phone", "profile"]
    
    def validate(self, attrs):
        return super().validate(attrs)

    def save(self, **kwargs):
        # Hash the password before saving
        password = self.validated_data.get("password")
        if password:
            self.validated_data["password"] = handler.hash(password)

        return super().save(**kwargs)



class AdminGETProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuth
        fields = ['id', 'f_name', 'l_name', 'email', 'address', 'phone', 'profile', 'role']


class AdminUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuth
        fields = ['f_name', 'l_name', 'address', 'phone', 'profile']


# CRUD ON BRAND 

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class AdminSer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuth
        fields = ['id', 'email', 'f_name', 'l_name', 'profile']

class GETBrandSerializer(serializers.ModelSerializer):
    creator_info= AdminSer(source= "admin_id")
    class Meta:
        model = Brand
        fields = ['id', 'created_at', 'name', 'text', 'image', 'creator_info']



# CRUD ON Product Category 

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class GETProductCategorySerializer(serializers.ModelSerializer):
    creator_info= AdminSer(source= "admin_id")
    class Meta:
        model = ProductCategory
        fields = ['id', 'created_at', 'name', 'image', 'creator_info',]


# CRUD ON BANNER

class GETBannerSerializer(serializers.ModelSerializer):
    creator_info= AdminSer(source= "admin_id")
    class Meta:
        model = ProductCategory
        fields = ['id', 'created_at', 'name', 'banner_text', 'banner_image', 'creator_info',]