import jwt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from typing import List

from models import User

config_credentials = dotenv_values('.env')

conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials['MAIL_USERNAME'],
    MAIL_PASSWORD=config_credentials['PASS'],
    MAIL_FROM=config_credentials['EMAIL'],
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email(email: List, instance: User):
    token_data = {
        'id': instance.id,
        'username': instance.username,
    }
    token = jwt.encode(payload=token_data, key=config_credentials['SECRET'], algorithm="HS256")
    html_content = f"""
    <!DOCTYPE html>
    <head>
        <title>Pug</title>
        <style>
            body {{
                background-color: #f9f9f9;
                padding-right: 10px;
                padding-left: 10px;
            }}

            .content {{
                background-color: #ffffff;
                border-color: #e5e5e5;
                border-style: solid;
                border-width: 0 1px 1px 1px;
                max-width: 600px;
                width: 100%;
                height: 420px;
                margin-top: 60.5px;
                margin-bottom: 31px;
                border-top: solid 3px #8e2de2;
                border-top: solid 3px -webkit-linear-gradient(to right, #8e2de2, #4a00e0);
                border-top: solid 3px -webkit-linear-gradient(to right, #8e2de2, #4a00e0);
                text-align: center;
                padding: 100px 0px 0px;
            }}

            h1 {{
                padding-bottom: 5px;
                color: #000;
                font-family: Poppins, Helvetica, Arial, sans-serif;
                font-size: 28px;
                font-weight: 400;
                font-style: normal;
                letter-spacing: normal;
                line-height: 36px;
                text-transform: none;
                text-align: center;
            }}

            h2 {{
                margin-bottom: 30px;
                color: #999;
                font-family: Poppins, Helvetica, Arial, sans-serif;
                font-size: 16px;
                font-weight: 300;
                font-style: normal;
                letter-spacing: normal;
                line-height: 24px;
                text-transform: none;
                text-align: center;
            }}

            p {{
                font-size: 14px;
                margin: 0px 21px;
                color: #666;
                font-family: 'Open Sans', Helvetica, Arial, sans-serif;
                font-weight: 300;
                font-style: normal;
                letter-spacing: normal;
                line-height: 22px;
                margin-bottom: 40px;
            }}

            .btn-primary {{
                background: #8e2de2;
                background: -webkit-linear-gradient(to right, #8e2de2, #4a00e0);
                background: linear-gradient(to right, #8e2de2, #4a00e0);
                border: none;
                font-family: Poppins, Helvetica, Arial, sans-serif;
                font-weight: 200;
                font-style: normal;
                letter-spacing: 1px;
                text-transform: uppercase;
                text-decoration: none;
            }}

            footer {{
                max-width: 600px;
                width: 100%;
                height: 420px;
                padding-top: 50px;
                text-align: center;
            }}

            small {{
                color: #bbb;
                font-family: 'Open Sans', Helvetica, Arial, sans-serif;
                font-size: 12px;
                font-weight: 400;
                font-style: normal;
                letter-spacing: normal;
                line-height: 20px;
                text-transform: none;
                margin-bottom: 5px;
                display: block;
            }}

            small:last-child {{
                margin-top: 20px;
            }}

            a {{
                color: #bbb;
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="d-flex align-items-center justify-content-center">
            <div class="content">
                <h1>Hello, {instance.username}!</h1>
                <h2>Verify Your Email Account</h2>
                <p>Thanks for creating your account on our platform! Please click on confirm button to validate your
                    account.</p>
                <button class="btn btn-primary btn-lg" type="button"
                        onclick="window.location.href='http://localhost:8000/verification/?token={token}';">
                    Confirm Email
                </button>
                <a href="http://localhost:8000/verification/?token={token}">Confirm Email</a>
            </div>
        </div>
        <div class="d-flex align-items-center justify-content-center">
            <footer>
                <small>Powered by Julien.js | A lightweight Node.js scaffold</small>
                <small><a href="#" target="_blank">View Web Version</a> | <a href="#" target="_blank">Email Preferences</a> | <a
                        href="#" target="_blank">Privacy Policy</a></small>
                <small>If you have any questions please contact us <a href="mailto:support@example.com" target="_blank">support@example.com</a>.<br><a
                        href="#" target="_blank">Unsubscribe</a> from our mailing lists.</small>
            </footer>
        </div>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="E-commerce",
        recipients=email,
        body=html_content,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message=message)
