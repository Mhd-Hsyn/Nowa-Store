
from decouple import config
import jwt, datetime
from adminapi.models import AdminAuth, AdminWhitelistToken
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


# def user_generated_token(fetchuser: UserAuth):
#     """
#     User Generate Token When User Login
#     """
#     try:
#         secret_key = config("USER_JWT_TOKEN")
#         totaldays = 1
#         token_payload = {
#             "id": str(fetchuser.id),
#             "email": fetchuser.email,
#             "exp": datetime.datetime.utcnow() + datetime.timedelta(days=totaldays),
#             "iat": datetime.datetime.utcnow(),
#         }
#         detail_payload = {
#             "id": str(fetchuser.id),
#             "email": fetchuser.email,
#             "fullname": fetchuser.full_name,
#         }

#         token = jwt.encode(token_payload, key=secret_key, algorithm="HS256")
#         return {"status": True, "token": token, "payload": detail_payload}
#     except Exception as e:
#         return {"status": False, "message": f"Error during generationg token {str(e)}"}



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



# def admin_blacklist_token(id, token):
#     try:
#         AdminWhitelistToken.objects.get(user=id, token=token).delete()
#         return True

#     except:
#         return False



