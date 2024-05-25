from uuid import UUID
from rest_framework import serializers
from .models import (
    AdminAuth
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