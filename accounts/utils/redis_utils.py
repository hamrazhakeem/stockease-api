import json
import uuid
import random
from django.core.cache import caches

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def store_user_data(email, password):
    token = str(uuid.uuid4())
    otp = generate_otp()
    
    user_data = {
        'email': email,
        'password': password,
        'otp': otp
    }
    
    # Use Django's cache API
    otp_cache = caches['otp_cache']
    otp_cache.set(f"user_registration:{token}", json.dumps(user_data))
    
    return token, otp

def get_user_data(token):
    """Retrieve user data from Redis using token"""
    key = f"user_registration:{token}"
    data = caches['otp_cache'].get(key)
    
    if not data:
        return None
    
    return json.loads(data)

def delete_user_data(token):
    """Delete user data from Redis after successful verification"""
    key = f"user_registration:{token}"
    caches['otp_cache'].delete(key)