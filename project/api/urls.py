from django.urls import path
from .views import RegisterView, VerifyOTPView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
]
    
