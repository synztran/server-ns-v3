import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from server.core.oauth2 import create_verification_token

load_dotenv()
hostMail = "noobassembly@gmail.com"
API_KEY = os.getenv("SENDGRID_API_KEY")
TEMPPLATE_VERIFY_ID = os.getenv("TEMPLATE_VERIFY_ID")

def send_mail_verify(request: dict, accountId: int):
    toMail = request.get("email")
    tokenVerify = create_verification_token(accountId)
    print("tokenVerify", tokenVerify)
    if not tokenVerify:
        return {
            "status": "Error",
            "message": "Token verify failed"
        }
    message = Mail(
        from_email=hostMail,
        to_emails=toMail,
        subject='Xác thực tài khoản từ NoobStore',
    )
    domain = "http://localhost:3000"
    link_verify = f"{domain}/verify?token={tokenVerify}"
    dynamic_template_data = {
        "link_verify": link_verify,
    }
    message.template_id = TEMPPLATE_VERIFY_ID
    message.dynamic_template_data = dynamic_template_data
    try:
        sg = SendGridAPIClient(API_KEY)
        response = sg.send(message)
        print(response.status_code)
        return {
            "status": "success",
            "message": "Mail sent successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Mail sent failed"
        }
