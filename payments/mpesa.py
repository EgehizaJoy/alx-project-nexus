import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_mpesa_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
    )
    return response.json().get("access_token")

import base64
import datetime

def stk_push_request(phone, amount, order_id):
    token = get_mpesa_token()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode("utf-8")
    ).decode("utf-8")

    api_url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": "https://4d57391c134a.ngrok-free.app/mpesa/callback/",
        "AccountReference": str(order_id),
        "TransactionDesc": f"Order {order_id} Payment",
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
