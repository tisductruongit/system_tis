from django.urls import path
from .views import UserRegisterView, UserProfileView, BusinessEmployeeListCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='api_register'),
    path('login/', TokenObtainPairView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('profile/', UserProfileView.as_view(), name='api_profile'),
    
    # API mới thêm cho quản lý nhân sự doanh nghiệp
    path('employees/', BusinessEmployeeListCreateView.as_view(), name='api_business_employees'),
]