from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from .models import User
from .serializers import UserSignupSerializer, OTPVerificationSerializer, UserLoginSerializer, EmailUpdateSerializer, PasswordChangeSerializer, UserProfileSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .utils.redis_utils import store_user_data, get_user_data, delete_user_data
from .utils.email_utils import send_otp_email
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework import generics
from .permissions import IsOwner
import logging

# Get logger for accounts app
logger = logging.getLogger('accounts')

class UserSignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        logger.info("Processing user signup request")
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if User.objects.filter(email=email).exists():
            logger.warning(f"Signup attempt with existing email: {email}")
            return Response(
                {"email": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token, otp = store_user_data(email, password)
        
        send_otp_email(email, otp)
        logger.info(f"OTP {otp} sent to {email} for verification")

        return Response({
            "message": "OTP sent to your email. Please verify to complete registration.",
            "token": token
        }, status=status.HTTP_200_OK)
    
class OTPVerificationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        logger.info("Processing OTP verification request")
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        otp = serializer.validated_data['otp']
        
        user_data = get_user_data(token)
        
        if not user_data:
            logger.warning(f"OTP verification with expired token")
            return Response(
                {"token": "Registration session expired. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user_data['otp'] != otp:
            logger.warning(f"Invalid OTP attempt for email: {user_data['email']}")
            return Response(
                {"otp": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )
        
        delete_user_data(token)
        logger.info(f"User registered successfully: {user.email}")

        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
class test_view(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        logger.debug("Test view accessed")
        return Response({"message": "Hello, World!"}, status=status.HTTP_200_OK)

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        logger.info("Processing login request")
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User logged in successfully: {user.email}")
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                },
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"Login failed: {str(e)}")
            # Let DRF handle the exception response
            raise
    
class UserLogoutView(APIView):    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out successfully: {request.user.email}")
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateEmailView(APIView):
    def put(self, request):
        logger.info(f"Processing email update request for user: {request.user.id}")
        serializer = EmailUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Get the new email
        new_email = serializer.validated_data['email']
        old_email = request.user.email
        
        # Update the user's email
        user = request.user
        user.email = new_email
        user.save()
        
        logger.info(f"Email updated from {old_email} to {new_email} for user: {user.id}")
        return Response({
            'message': 'Email updated successfully',
            'email': new_email
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    def put(self, request):
        logger.info(f"Processing password change request for user: {request.user.id}")
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Change the password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"Password changed successfully for user: {user.id}")
        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)

class UserList(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        logger.info(f"Admin user {request.user.id} listing all users")
        return super().list(request, *args, **kwargs)

class UserDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    """
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsOwner]

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"User {request.user.id} retrieving profile for user {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)