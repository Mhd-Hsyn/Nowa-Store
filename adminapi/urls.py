from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index,
    UserAuthViewset,
    AdminProfileViewset,
    SuperAdminRole
)

router = DefaultRouter()
router.register("auth", UserAuthViewset, basename="auth")
router.register("profile", AdminProfileViewset, basename="profile")
router.register("superadmin", SuperAdminRole, basename="speradmin")

urlpatterns = [
    path("", index),
]

urlpatterns += router.urls
