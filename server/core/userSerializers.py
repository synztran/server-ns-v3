def user_entity(user):
    if "verified_at" in user:
        # Check if the value of "verified_at" is a string
        if isinstance(user["verifiedAt"], str):
            formatActiveDate = user["verifiedAt"]
        else:
            formatActiveDate = ""
    else:
        formatActiveDate = ""

    return {
        "customerId": user["customerId"],
        "accountId": user["accountId"],
        "email": user["email"],
        # "password": user["password"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "dob": user["dob"] if "dob" in user else "",
        "shippingAt": [
            {
                "firstName": item.get("firstName", ""),
                "lastName": item.get("lastName", ""),
                "companyName": item.get("cname", ""),
                "email": item.get("email", ""),
                "townCity": item.get("townCity", ""),
                "phoneNumber": item.get("phoneNumber", ""),
                "address": item.get("address", ""),
                "country": item.get("country", ""),
                "zipCode": item.get("zipCode", "")
            } for item in user["shippingAt"]
        ] if "shippingAt" in user else [],
        "phoneAreaCode": user["phoneAreaCode"] if "phoneAreaCode" in user else "",
        "phoneNumber": user["phoneNumber"] if "phoneNumber" in user else "",
        "createdAt": user["createdAt"],
        "updatedAt": user["updatedAt"],
        "verified": user["verified"],
        "verifiedAt": formatActiveDate,
        "getNoty": user["getNoty"] if "getNoty" in user else False,
        "paypal": user["paypal"] if "paypal" in user else "",
        "fbUrl": user["fbUrl"] if "fbUrl" in user else "",
        "cartId": user["cartId"] if "cartId" in user else "",
        "avatar": user["avatar"] if "avatar" in user else "",
    }

def userResponseEntity(user) -> dict:
    return {
        "customerId": user["customerId"],
        "accountId": user["accountId"],
        "email": user["email"],
        "fname": user["fname"],
        "lname": user["lname"],
        "dob": user["dob"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "role": user["role"],
    }

def embeddedUserResponse(user) -> dict:
    return {
        "customerId": user["customerId"],
        "accountId": user["accountId"],
        "email": user["email"],
        "fname": user["fname"],
        "lname": user["lname"],
    }

def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
