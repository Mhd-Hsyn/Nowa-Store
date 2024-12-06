import random
from django.shortcuts import render
from uuid import UUID
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import status
from decouple import config
from django.conf import settings
from passlib.hash import django_pbkdf2_sha256 as handler
from core.helper import (
    key_validation,
    exception_handler,
    check_emailforamt,
    password_length_validator
)
from core.token import (
    admin_generated_token,
    admin_blacklist_token
)
from core.sendemail import sendotp
from core.permissions import (
    SuperAdminSpecificPermission,
    AdminPermission
)
from .models import *
from .serializers import *
from .pagination import *



def index(request):
    return HttpResponse("<h1>Project Ecommerce Shop</h1>")




class UserAuthViewset(ModelViewSet):
    @action(detail=False, methods=["post"])
    def login(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]

            fetch_admin = AdminAuth.objects.filter(email=email).first()

            if fetch_admin and handler.verify(password, fetch_admin.password):
                generate_auth = admin_generated_token(fetch_admin)

                if generate_auth["status"]:
                    fetch_admin.save()
                    return Response(
                        {
                            "status": True,
                            "message": "Login SuccessFully",
                            "token": generate_auth["token"],
                            "data": generate_auth["payload"],
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(generate_auth)
            else:
                return Response(
                    {"status": False, "message": "Invalid Credential"}, status=401
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def send_forget_otp(self, request):
        try:
            requireFields = ["email"]
            validator = key_validation(True, True, request.data, requireFields)
            if validator:
                return Response(validator, status=status.HTTP_400_BAD_REQUEST)

            else:
                email = request.data["email"]
                emailstatus = check_emailforamt(email)
                if not emailstatus:
                    return Response(
                        {"status": False, "message": "Email format is incorrect"}
                    )

                fetchuser = AdminAuth.objects.filter(email=email).first()
                if fetchuser:
                    token = random.randrange(100000, 999999, 6)
                    fetchuser.otp = token
                    fetchuser.otp_count = 0
                    fetchuser.otp_status = True
                    fetchuser.save()
                    emailstatus = sendotp(email,token)
                    if emailstatus:
                        return Response(
                            {
                                "status": True,
                                "message": "Email send successfully",
                                "email": fetchuser.email,
                                "otp": token
                            }
                        )

                    else:
                        return Response(
                            {"status": False, "message": "Something went wrong"},status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response({"status": False, "message": "Email doesnot exist"},status=404)

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["POST"])
    def verify_otp(self, request):
        try:
            ##validator keys and required
            requireFields = ["otp", "email"]
            validator = key_validation(True, True, request.data, requireFields)

            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)

            else:
                otp = request.data["otp"]
                email = request.data["email"]
                fetchuser = AdminAuth.objects.filter(email=email).first()
                if fetchuser:
                    if fetchuser.otp_status and fetchuser.otp_count < 3:
                        if fetchuser.otp == int(otp):
                            fetchuser.otp = 0
                            fetchuser.otp_status = True
                            fetchuser.save()
                            return Response(
                                {
                                    "status": True,
                                    "message": "Otp verified",
                                    "email": str(fetchuser.email),
                                },
                                status=status.HTTP_200_OK,
                            )
                        else:
                            fetchuser.otp_count += 1
                            fetchuser.save()
                            if fetchuser.otp_count >= 3:
                                fetchuser.otp = 0
                                fetchuser.otp_count = 0
                                fetchuser.otp_status = False
                                fetchuser.save()
                                return Response(
                                    {
                                        "status": False,
                                        "message": f"Your OTP is expired . . . Kindly get OTP again",
                                    },status=status.HTTP_400_BAD_REQUEST
                                )
                            return Response(
                                {
                                    "status": False,
                                    "message": f"Your OTP is wrong . You have only {3- fetchuser.otp_count} attempts left ",
                                },status=status.HTTP_400_BAD_REQUEST
                            )
                    return Response(
                        {
                            "status": False,
                            "message": "Your OTP is expired . . . Kindly get OTP again",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response(
                    {"status": False, "message": "User not exist"}, status=404
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["POST"])
    def reset_password(self, request):
        try:
            requireFeild = ["email", "newpassword"]
            validator = key_validation(True, True, request.data, requireFeild)
            if validator:
                return Response(validator, status=status.HTTP_400_BAD_REQUEST)

            email = request.data["email"]
            newpassword = request.data["newpassword"]
            if not password_length_validator(newpassword):
                return Response(
                    {
                        "status": False,
                        "error": "Password length must be greater than 8",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            fetchuser = AdminAuth.objects.filter(email=email).first()
            if fetchuser:
                if fetchuser.otp_status and fetchuser.otp == 0:
                    fetchuser.password = handler.hash(newpassword)
                    fetchuser.otp_status = False
                    fetchuser.otp_count = 0
                    fetchuser.save()
                    return Response(
                        {
                            "status": True,
                            "message": "Password updates successfully ",
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": False, "message": "Token not verified !!!!"}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"status": False, "message": "User Not Exist !!!"}, status=404
            )
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class AdminProfileViewset(ModelViewSet):
    permission_classes = [AdminPermission]
    
    @action(detail=False, methods=["GET"])
    def logout(self, request):
        try:
            admin_id = request.auth['id']  # access from permission class after decode
            admin_blacklist_token(admin_id, request)
            return Response({"status": True, "message": "Logout Successfully"}, status=200)
        except Exception as e:
            return Response({"status": False, "message": f"Something wrong {str(e)}"}, status=200)


    @action(detail=False, methods=['GET'])
    def get_profile(self, request):
        try:
            id = request.auth.get("id")
            fetchuser = AdminAuth.objects.filter(id=id).first()
            ser= AdminGETProfileSerializer(instance= fetchuser)
            return Response({"status": True, "data": ser.data})
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)
        
    @action(detail=False,methods=["PUT"])
    def update_profile(self, request):
        try:
            user_id = request.auth['id']
            fetchuser = AdminAuth.objects.filter(id=user_id).first()
            ser = AdminUpdateProfileSerializer(instance= fetchuser, data= request.data)
            if ser.is_valid():
                ser.save()
                return Response(
                    {
                        "status": True,
                        "message": "Updated Successfully",
                        "data": AdminGETProfileSerializer(fetchuser).data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                message= exception_handler(ser)
                return Response({"status": False, "message": message},status=status.HTTP_400_BAD_REQUEST,)
                        
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)


    @action(detail=False, methods=["POST"])
    def change_password(self, request):
        try:
            requireFeilds = ["oldpassword", "newpassword"]
            validator = key_validation(True, True, request.data, requireFeilds)
            if validator:
                return Response(validator, status=400)

            admin_id = request.auth['id']
            fetchuser = AdminAuth.objects.filter(id=admin_id).first()
            chk_pass = handler.verify(request.data["oldpassword"], fetchuser.password)
            if chk_pass:
                if password_length_validator(request.data["newpassword"]):
                    fetchuser.password = handler.hash(request.data["newpassword"])
                    # delete old token
                    admin_blacklist_token(fetchuser, request)
                    # generate new token
                    token = admin_generated_token(fetchuser)
                    fetchuser.save()
                    return Response(
                        {
                            "status": True,
                            "message": "Password Successfully Changed",
                            "token": token["token"],
                        },
                        status=200,
                    )
                return Response({"status": False, "message": "Password must contain at least one special character and one uppercase letter, and be between 8 and 20 characters long"}, status=400)
            return Response({"status": False, "message": "Old Password not verified"}, status=400)
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=400)
    



class SuperAdminRole(ModelViewSet):
    permission_classes=[SuperAdminSpecificPermission]

    @action(detail=False, methods=["POST"])
    def add_manager(self, request):
        try:
            required_fields = ["f_name", "l_name", "email", "password"]
            validator = key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            admin_ser = AdminRegisterSerializer(data=request.data)
            if admin_ser.is_valid():
                admin_ser.save()

                return Response(
                    {"status": True, "message": "Manager Account created successfully"},
                    status=status.HTTP_201_CREATED,
                )

            else:
                error_message = exception_handler(admin_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=["GET"])
    def get_manager(self, request):
        try:
            fetch_managers= AdminAuth.objects.filter(role="Manager")

            admin_ser = AdminGETProfileSerializer(instance=fetch_managers, many=True)
            return Response(
                {"status": True, "data": admin_ser.data},
                status=status.HTTP_200_OK,
            )

           
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=["DELETE"])
    def delete_manager(self, request):
        try:
            required_fields = ["manager_id"]
            validator = key_validation(True, True, request.GET, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            fetch_managers= AdminAuth.objects.get(id=request.GET.get("manager_id"))
            fetch_managers.delete()

            return Response(
                {"status": True, "message": "Manager Deleted Successfully"},
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(
                {"status": False, "message": "Manager not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CRUD on Brand
class BrandApiView(APIView):
    permission_classes= [AdminPermission]

    def post(self, request):
        try:
            admin_id=  request.auth.get('id')
            required_fields= ['name', 'text', 'image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            data= request.data
            data['admin_id']= admin_id
            brand_ser= BrandSerializer(data= data)
            if brand_ser.is_valid():
                brand_ser.save()
                return Response(
                    {"status": True, "message": "Brand created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                error_message = exception_handler(brand_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def get(self, request):
        try:
            all_brands = Brand.objects.all()
            paginator = BrandPagination()  # Use your custom paginator
            paginated_brands = paginator.paginate_queryset(all_brands, request)
            brands_ser = GETBrandSerializer(paginated_brands, many=True)
            return paginator.get_paginated_response(brands_ser.data)
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def put(self, request):
        try:
            required_fields= ['id', 'name', 'text', 'image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_brand= Brand.objects.filter(id= request.data.get('id')).first()
            if not fetch_brand:
                return Response(
                    {"status": False, "message": "Brand not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            brand_ser= BrandSerializer(instance=fetch_brand, data= request.data)
            if brand_ser.is_valid():
                brand_ser.save()
                return Response(
                    {"status": True, "message": "Brand Updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                error_message = exception_handler(brand_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        try:
            admin_id=  request.auth.get('id')
            required_fields= ['id']
            validator= key_validation(True, True, request.GET, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_brand= Brand.objects.filter(id= request.GET.get('id')).first()
            if not fetch_brand:
                return Response(
                    {"status": False, "message": "Brand not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            fetch_brand.delete()
            return Response(
                {"status": True, "message": "Brand Updated successfully"},
                status=status.HTTP_200_OK,
            )
           
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# CRUD on Product-Category
class ProductCategoryApiView(APIView):
    permission_classes= [AdminPermission]

    def post(self, request):
        try:
            admin_id=  request.auth.get('id')
            required_fields= ['name', 'image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            data= request.data
            data['admin_id']= admin_id
            p_cat_ser= ProductCategorySerializer(data= data)
            if p_cat_ser.is_valid():
                p_cat_ser.save()
                return Response(
                    {"status": True, "message": "Product Category created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                error_message = exception_handler(p_cat_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def get(self, request):
        try:
            all_brands = ProductCategory.objects.filter(is_banner=False)
            paginator = ProductCategoryPagination()  # Use your custom paginator
            paginated_brands = paginator.paginate_queryset(all_brands, request)
            brands_ser = GETProductCategorySerializer(paginated_brands, many=True)
            return paginator.get_paginated_response(brands_ser.data)
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def put(self, request):
        try:
            required_fields= ['id', 'name', 'image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_p_cate= ProductCategory.objects.filter(id= request.data.get('id')).first()
            if not fetch_p_cate:
                return Response(
                    {"status": False, "message": "Product Category not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            p_cat_ser= ProductCategorySerializer(instance=fetch_p_cate, data= request.data)
            if p_cat_ser.is_valid():
                p_cat_ser.save()
                return Response(
                    {"status": True, "message": "Product Category Updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                error_message = exception_handler(p_cat_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        try:
            required_fields= ['id']
            validator= key_validation(True, True, request.GET, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_p_cate= ProductCategory.objects.filter(id= request.GET.get('id')).first()
            if not fetch_p_cate:
                return Response(
                    {"status": False, "message": "Product Category not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fetch_p_cate.delete()
            return Response(
                {"status": True, "message": "Product Category Deleted successfully"},
                status=status.HTTP_200_OK,
            )
           
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# CRUD ON BANNER
class BannerApiView(APIView):
    permission_classes= [AdminPermission]

    def post(self, request):
        try:
            admin_id=  request.auth.get('id')
            required_fields= ['name', 'banner_text', 'banner_image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            data= request.data
            data['admin_id']= admin_id
            data['is_banner']= True
            p_cat_ser= ProductCategorySerializer(data= data)
            if p_cat_ser.is_valid():
                p_cat_ser.save()
                return Response(
                    {"status": True, "message": "Banner created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                error_message = exception_handler(p_cat_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    def get(self, request):
        try:
            all_brands = ProductCategory.objects.filter(is_banner=True)
            paginator = ProductCategoryPagination()  # Use your custom paginator
            paginated_brands = paginator.paginate_queryset(all_brands, request)
            brands_ser = GETBannerSerializer(paginated_brands, many=True)
            return paginator.get_paginated_response(brands_ser.data)
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def put(self, request):
        try:
            required_fields= ['id', 'name', 'banner_text', 'banner_image']
            validator= key_validation(True, True, request.data, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_p_cate= ProductCategory.objects.filter(id= request.data.get('id')).first()
            if not fetch_p_cate:
                return Response(
                    {"status": False, "message": "Banner not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data= request.data
            data['is_banner']= True
            p_cat_ser= ProductCategorySerializer(instance=fetch_p_cate, data= request.data)
            if p_cat_ser.is_valid():
                p_cat_ser.save()
                return Response(
                    {"status": True, "message": "Banner Updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                error_message = exception_handler(p_cat_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        try:
            required_fields= ['id']
            validator= key_validation(True, True, request.GET, required_fields)
            if validator:
                return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
            fetch_p_cate= ProductCategory.objects.filter(id= request.GET.get('id')).first()
            if not fetch_p_cate:
                return Response(
                    {"status": False, "message": "Banner not exists with this ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fetch_p_cate.delete()
            return Response(
                {"status": True, "message": "Banner Deleted successfully"},
                status=status.HTTP_200_OK,
            )
           
        except Exception as e:
            message = {"status": False}
            message.update(message=str(e)) if settings.DEBUG else message.update(
                message="Internal server error"
            )
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class ProductApiView(ModelViewSet):
    permission_classes= [AdminPermission]

    @action(detail= False, methods=['POST'])
    def add_product(self, request):
        # try:
            admin_id=  request.auth.get('id')
            print(admin_id)
            data= request.data.copy()
            # data['admin_id']= admin_id

            print("data ______ ", data)
            product_ser= AddProductSerializer(data= data, context={'admin_id': admin_id})
            if product_ser.is_valid():
                product_ser.save()
                return Response(
                    {"status": True, "message": "Product created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                error_message = exception_handler(product_ser)
                return Response(
                    {"status": False, "message": error_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # except Exception as e:
        #     message = {"status": False}
        #     message.update(message=str(e)) if settings.DEBUG else message.update(
        #         message="Internal server error"
        #     )
        #     return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    # def get(self, request):
    #     try:
    #         all_brands = ProductCategory.objects.filter(is_banner=True)
    #         paginator = ProductCategoryPagination()  # Use your custom paginator
    #         paginated_brands = paginator.paginate_queryset(all_brands, request)
    #         brands_ser = GETBannerSerializer(paginated_brands, many=True)
    #         return paginator.get_paginated_response(brands_ser.data)
    #     except Exception as e:
    #         message = {"status": False}
    #         message.update(message=str(e)) if settings.DEBUG else message.update(
    #             message="Internal server error"
    #         )
    #         return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # def put(self, request):
    #     try:
    #         required_fields= ['id', 'name', 'banner_text', 'banner_image']
    #         validator= key_validation(True, True, request.data, required_fields)
    #         if validator:
    #             return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
    #         fetch_p_cate= ProductCategory.objects.filter(id= request.data.get('id')).first()
    #         if not fetch_p_cate:
    #             return Response(
    #                 {"status": False, "message": "Banner not exists with this ID"},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )
    #         data= request.data
    #         data['is_banner']= True
    #         p_cat_ser= ProductCategorySerializer(instance=fetch_p_cate, data= request.data)
    #         if p_cat_ser.is_valid():
    #             p_cat_ser.save()
    #             return Response(
    #                 {"status": True, "message": "Banner Updated successfully"},
    #                 status=status.HTTP_200_OK,
    #             )
    #         else:
    #             error_message = exception_handler(p_cat_ser)
    #             return Response(
    #                 {"status": False, "message": error_message},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )
            
    #     except Exception as e:
    #         message = {"status": False}
    #         message.update(message=str(e)) if settings.DEBUG else message.update(
    #             message="Internal server error"
    #         )
    #         return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # def delete(self, request):
    #     try:
    #         required_fields= ['id']
    #         validator= key_validation(True, True, request.GET, required_fields)
    #         if validator:
    #             return Response(validator,status=status.HTTP_400_BAD_REQUEST)
            
    #         fetch_p_cate= ProductCategory.objects.filter(id= request.GET.get('id')).first()
    #         if not fetch_p_cate:
    #             return Response(
    #                 {"status": False, "message": "Banner not exists with this ID"},
    #                 status=status.HTTP_400_BAD_REQUEST,
    #             )

    #         fetch_p_cate.delete()
    #         return Response(
    #             {"status": True, "message": "Banner Deleted successfully"},
    #             status=status.HTTP_200_OK,
    #         )
           
    #     except Exception as e:
    #         message = {"status": False}
    #         message.update(message=str(e)) if settings.DEBUG else message.update(
    #             message="Internal server error"
    #         )
    #         return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


