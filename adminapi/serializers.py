from django.utils import timezone
from uuid import UUID
from rest_framework import serializers
from .models import (
    AdminAuth,
    Brand,
    ProductCategory,
    Product,
    ProductImage
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
        fields = ['id', 'created_at', 'name', 'banner_text', 'banner_image', 'creator_info']


# CRUD ON PRODUCT

class AddProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
    )
    class Meta:
        model = Product
        fields =  [
            'category', 'brand', 'name', 'description', 'stock', 'overview', 
            'specification', 'price', 'discounted_price', 'is_discount',
            'discount_date_start', 'discount_date_end', 'delivery_info', 'images'
        ]
        extra_kwargs = {
            'category': {'required': False},
            'brand': {'required': False},
            'name': {'required': True},
            'description': {'required': True},
            'stock': {'required': True},
            'overview': {'required': True},
            'specification': {'required': True},
            'price': {'required': True},
            'discounted_price': {'required': False},
            'is_discount': {'required': False},
            'discount_date_start': {'required': False},
            'discount_date_end': {'required': False},
            'delivery_info': {'required': False},
            'admin_id': {'required': True}
        }
    
    def validate(self, attrs):
        category = attrs.get('category')
        brand = attrs.get('brand')
        if not category and not brand:
            raise serializers.ValidationError("Either category or brand must be provided.")
        
        admin_id = self.context.get('admin_id') 
        attrs['admin_id'] = AdminAuth.objects.filter(id=admin_id).first()


        discount_keys = ['discounted_price', 'discount_date_start', 'discount_date_end']
        if any(key in attrs for key in discount_keys):
            # Ensure all discount keys are provided in attrs
            for key in discount_keys:
                if key not in attrs:
                    raise serializers.ValidationError(f"'{key}' must be provided if any discount information is included.")
        
        discounted_price = attrs.get('discounted_price')
        discount_date_start = attrs.get('discount_date_start')
        discount_date_end = attrs.get('discount_date_end')
        price = attrs.get('price')
    
        if discounted_price and discount_date_start and discount_date_end:
            if discount_date_start > discount_date_end:
                raise serializers.ValidationError("Discount date start must be before the end date.")
            
            if discounted_price > price:
                raise serializers.ValidationError("Discounted price cannot be more than the original price.")
            
            # Ensure the discount dates are valid (i.e., both start and end dates are in the future)
            current_date = timezone.now()   # Get today's date (without time)
            if discount_date_end < current_date:
                raise serializers.ValidationError("Discount end dates must be in the future.")
            
            attrs['is_discount'] = True

        return attrs


    def validate_images(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("At least 3 images are required.")
        return value

    def create(self, validated_data):
        images = validated_data.pop('images')
        product = Product.objects.create(**validated_data)
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return product
        
            

