from rest_framework import serializers
from passlib.hash import django_pbkdf2_sha256 as handler
from django.contrib.auth.hashers import make_password
from .models import *
from core.helper import (
    key_validation,
    exception_handler,
    check_emailforamt,
    password_length_validator
)

class UserSignUpSerializer(serializers.ModelSerializer):
    """
    Only use of this Serializer for Signup of a user
    This create also the Company name with User creation account
    also check the "company_name" before creating a user and the company creation
    """
    # also add the company with account creation
    class Meta:
        model = User
        fields = ['fname', 'lname', 'email', 'password', 'contact', 'profile']
    
    def validate_email(self, value):
        if not check_emailforamt(value):
            raise serializers.ValidationError("Email Format Is Incorrect")
        return value
    
    def validate_password(self, value):
        if not password_length_validator(value):
            raise serializers.ValidationError("Password must contain at least one special character and one uppercase letter, and be between 8 and 20 characters long")
        hashed_password = handler.hash(value)
        return hashed_password
    
    def create(self, validated_data):
       
        user = User.objects.create(**validated_data)
        return user




class UserGETProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fname', 'lname', 'email', 'address', 'contact', 'profile']


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fname', 'lname', 'address', 'contact', 'profile']

