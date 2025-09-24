import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
resp = requests.get(
    url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
)
print(resp.status_code, resp.text)
