import requests
from datetime import datetime
import base64
from django.conf import settings
import json

class MpesaClient:
    def __init__(self):
        self.business_shortcode = settings.MPESA_BUSINESS_SHORTCODE
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        
        if settings.MPESA_ENVIRONMENT == 'sandbox':
            self.base_url = 'https://sandbox.safaricom.co.ke'
        else:
            self.base_url = 'https://api.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth}'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['access_token']
        return None
    
    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode(), timestamp
    
    def initiate_stk_push(self, phone_number, amount, reference, callback_url):
        """Initiate STK push payment"""
        access_token = self.get_access_token()
        if not access_token:
            return None, "Failed to get access token"
        
        password, timestamp = self.generate_password()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.business_shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.business_shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': callback_url,
            'AccountReference': reference,
            'TransactionDesc': f'Payment for order {reference}'
        }
        
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ResponseCode') == '0':
                return result, None
        
        return None, "Failed to initiate payment"
    
    def verify_transaction(self, checkout_request_id):
        """Verify transaction status"""
        access_token = self.get_access_token()
        if not access_token:
            return None, "Failed to get access token"
        
        password, timestamp = self.generate_password()
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.business_shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json(), None
        
        return None, "Failed to verify transaction"