from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import random
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, OTP

class RegisterView(APIView):
    def post(self, request):
        print("Request data:", request.data)

        # Extract data from the request
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        middle_name = request.data.get('middle_name')
        last_name = request.data.get('last_name')
        gender = request.data.get('gender')
        email = request.data.get('email')
        contact_number = request.data.get('contact_number')
        dob = request.data.get('dob')
        password = request.data.get('password')

        # Validate that required fields are present
        required_fields = ['username', 'first_name', 'email', 'middle_name', 'last_name', 'contact_number', 'dob', 'password']
        for field in required_fields:
            if not request.data.get(field):
                return Response({f'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username or email already exists
        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new user
        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender=gender,
            email=email,
            contact_number=contact_number,
            dob=dob,
        )
        
        user.set_password(password)
        user.save()

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        
        otp_instance = OTP.objects.create(user=user, otp_code=otp_code)

        # Send OTP email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp_code}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response({'message': 'User registered successfully. Please verify OTP.'}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        try:
            otp_record = OTP.objects.get(user=user, otp_code=otp)
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp_record.is_verified = True
        otp_record.save()
        user.otp_verified = True
        user.save()

        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check password and otp_verified
        if user.check_password(password) and user.otp_verified:
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials or user not verified."}, status=status.HTTP_401_UNAUTHORIZED)

# Optional: You can keep the send_otp_email function if needed elsewhere
def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)