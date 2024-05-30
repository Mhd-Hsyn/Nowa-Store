
from decouple import config
import jwt, datetime
from adminapi.models import AdminAuth, AdminWhitelistToken
from webapi.models import User, UserWhitelistToken
from django.conf import settings


def admin_generated_token(fetchuser: AdminAuth):
    authKey= config("ADMIN_JWT_TOKEN")
    totaldays= 100
    try:
        access_token_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
            "iat": datetime.datetime.utcnow(),
        }

        userpayload = {
            "id": str(fetchuser.id),
            "f_name": fetchuser.f_name,
            "l_name": fetchuser.l_name,
            "email": fetchuser.email,
            "profile": fetchuser.profile.url,
            "role": fetchuser.role
        }

        access_token = jwt.encode(access_token_payload, authKey, algorithm="HS256")
        AdminWhitelistToken.objects.create(admin_id= fetchuser, token = access_token)
        return {"status": True, "token": access_token, "payload": userpayload}

    except Exception as e:
        return {
            "status": False,
            "message": "Something went wrong in token creation",
            "details": str(e),
        }


def user_generated_token(fetchuser: User):
    """
    User Generate Token When User Login
    """
    try:
        secret_key = config("USER_JWT_TOKEN")
        totaldays = 1
        access_token_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
            "iat": datetime.datetime.utcnow(),
        }
        detail_payload = {
            "id": str(fetchuser.id),
            "email": fetchuser.email,
            "fname": fetchuser.fname,
            "lname": fetchuser.lname,
            "profile": fetchuser.profile.url,
        }

        access_token = jwt.encode(access_token_payload, key=secret_key, algorithm="HS256")
        UserWhitelistToken.objects.create(user= fetchuser, token = access_token)
        return {"status": True, "token": access_token, "payload": detail_payload}
    except Exception as e:
        return {"status": False, "message": f"Error during generationg token {str(e)}"}



def admin_blacklist_token(admin_id, request):
    try:
        token = request.META["HTTP_AUTHORIZATION"][7:]
        whitelist_token = AdminWhitelistToken.objects.filter(admin_id = admin_id, token = token).first()
        if not whitelist_token:
            return {'staus': False, "message": "token not found"}

        whitelist_token.delete()
        admin_all_tokens = AdminWhitelistToken.objects.filter(admin_id = admin_id)
        for fetch_token in admin_all_tokens:
            try:
                decode_token = jwt.decode(fetch_token.token, config('ADMIN_JWT_TOKEN'), "HS256")
            except:    
                fetch_token.delete()
        return True
    except Exception :
        return False


def user_blacklist_token(user_id, request):
    try:
        token = request.META["HTTP_AUTHORIZATION"][7:]
        whitelist_token = UserWhitelistToken.objects.filter(user = user_id, token = token).first()
        if not whitelist_token:
            return {'staus': False, "message": "token not found"}

        whitelist_token.delete()
        user_all_tokens = AdminWhitelistToken.objects.filter(user = user_id)
        for fetch_token in user_all_tokens:
            try:
                decode_token = jwt.decode(fetch_token.token, config('USER_JWT_TOKEN'), "HS256")
            except:    
                fetch_token.delete()
        return True
    except Exception :
        return False
