from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = 'Your OTP for StockEase Registration'
    message = f'Your OTP for registration is: {otp}. It will expire in 5 minutes.'
    
    return send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )