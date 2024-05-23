from rest_framework import permissions
from rest_framework.exceptions import APIException
from rest_framework.exceptions import AuthenticationFailed
from decouple import config
from adminapi.models import  AdminAuth, AdminWhitelistToken
import jwt


class SuperAdminSpecificPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            auth_token = request.META["HTTP_AUTHORIZATION"][7:]
            decode_token = jwt.decode(auth_token, config('ADMIN_JWT_TOKEN'), "HS256")
            whitelist = AdminWhitelistToken.objects.filter(
                admin_id =  decode_token['id'],
                token = auth_token,
                admin_id__role= "SuperAdmin"            # check Amdin is SuperAdmin
                ).first()
            if not whitelist:
                raise AuthenticationFailed(
                    {"status": False, "message": "SuperAdmin Not Authorize"}
                )
            request.auth = decode_token
            return True
        except AuthenticationFailed as af:
            raise af
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed({"status": False,"error":"Session Expired !!"})
        except jwt.DecodeError:
            raise AuthenticationFailed({"status": False,"error":"Invalid token"})
        except Exception as e:
            raise AuthenticationFailed({"status": False,"error":"Need Login", "exception": e})



class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            auth_token = request.META["HTTP_AUTHORIZATION"][7:]
            decode_token = jwt.decode(auth_token, config('ADMIN_JWT_TOKEN'), "HS256")
            whitelist = AdminWhitelistToken.objects.filter(
                admin_id =  decode_token['id'],
                token = auth_token,
                ).first()
            if not whitelist:
                raise AuthenticationFailed(
                    {"status": False, "message": "Admin Not Authorize"}
                )
            request.auth = decode_token
            return True
        except AuthenticationFailed as af:
            raise af
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed({"status": False,"error":"Session Expired !!"})
        except jwt.DecodeError:
            raise AuthenticationFailed({"status": False,"error":"Invalid token"})
        except Exception as e:
            raise AuthenticationFailed({"status": False,"error":"Need Login", "exception": e})