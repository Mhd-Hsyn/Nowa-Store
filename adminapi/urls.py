from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index,
    UserAuthViewset,
    AdminProfileViewset,
    SuperAdminRole,
    BrandApiView,
    # ProductCategoryApiView,
    # BannerApiView
)

router = DefaultRouter()
router.register("auth", UserAuthViewset, basename="auth")
router.register("profile", AdminProfileViewset, basename="profile")
router.register("superadmin", SuperAdminRole, basename="speradmin")

urlpatterns = [
    path("", index),
    path("brands/", BrandApiView.as_view()),
    # path("product-category/", ProductCategoryApiView.as_view()),
    # path("banner/", BannerApiView.as_view()),
]

urlpatterns += router.urls
