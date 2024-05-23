import jwt
import datetime
import re
import random
from adminapi.models import AdminAuth, AdminWhitelistToken
from PIL import Image
from decouple import config
import string
import secrets


def requireKeys(reqArray, requestData):
    try:
        for j in reqArray:
            if not j in requestData:
                return False
        return True

    except:
        return False


def allfieldsRequired(reqArray, requestData):
    try:
        for j in reqArray:
            if len(requestData[j]) == 0:
                return False

        return True

    except:
        return False


def check_emailforamt(email):
    emailregix = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    if re.match(emailregix, email):
        return True

    else:
        return False


def password_length_validator(passwd):
    if len(passwd) >= 8 and len(passwd) <= 20:
        return True

    else:
        return False


##both keys and required field validation


def key_validation(keyStatus, reqStatus, requestData, requireFields):
    ##keys validation
    if keyStatus:
        keysStataus = requireKeys(requireFields, requestData)
        if not keysStataus:
            return {
                "status": False,
                "message": f"{requireFields} all keys are required",
            }

    ##Required field validation
    if reqStatus:
        requiredStatus = allfieldsRequired(requireFields, requestData)
        if not requiredStatus:
            return {"status": False, "message": "All Fields are Required"}


def makedict(obj, key, imgkey=False):
    dictobj = {}

    for j in range(len(key)):
        keydata = getattr(obj, key[j])
        if keydata:
            dictobj[key[j]] = keydata

    if imgkey:
        imgUrl = getattr(obj, key[-1])
        if imgUrl:
            dictobj[key[-1]] = imgUrl.url
        else:
            dictobj[key[-1]] = ""

    return dictobj


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = "".join(secrets.choice(characters) for _ in range(length))
    return password


def exception_handler(val):
    error_messages = []

    if isinstance(val, dict):
        # If val is a dictionary, assume it's a custom validation result
        if "error" in val:
            error_messages.append(val["error"])
    else:
        # Otherwise, assume it's a serializer with errors attribute
        for field, errors in val.errors.items():
            # Customize the way you want to format each error message
            error_message = f"{field}: {', '.join(errors)}"
            error_messages.append(error_message)

    return ", ".join(error_messages)


def execption_handler(val):
    if "error" in val.errors:
        error = val.errors["error"][0]
    else:
        key = next(iter(val.errors))
        error = key + ", " + val.errors[key][0]

    return error

