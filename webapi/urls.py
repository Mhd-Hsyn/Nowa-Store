from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *


router= DefaultRouter()
router.register("auth", UserAuthViewset, basename="auth")
router.register("userprofile", UserProfileViewset, basename="userprofile")


urlpatterns = [
    path("", index),
    
]

urlpatterns += router.urls
