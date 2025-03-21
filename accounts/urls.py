from django.urls import path
from .views import UserSignupView, OTPVerificationView, UserLoginView, UserLogoutView, UpdateEmailView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('update-email/', UpdateEmailView.as_view(), name='update_email'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]