from rest_framework import generics, permissions, serializers
from .models import CustomUser, BusinessEmployee
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    BusinessEmployeeSerializer
)
# Import file quyền vừa tạo
from .permissions import IsBusinessRole

# ==========================================
# API ĐĂNG KÝ VÀ QUẢN LÝ PROFILE CÁ NHÂN
# ==========================================

class UserRegisterView(generics.CreateAPIView):
    """API Đăng ký tài khoản (Ai cũng gọi được)"""
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileView(generics.RetrieveUpdateAPIView):
    """API Xem và Cập nhật Profile (Phải đăng nhập)"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Tự động trả về profile của chính người đang gọi API
        return self.request.user


# ==========================================
# API DÀNH RIÊNG CHO DOANH NGHIỆP
# ==========================================

class BusinessEmployeeListCreateView(generics.ListCreateAPIView):
    """
    API Xem danh sách và Thêm nhân viên
    Chỉ cho phép tài khoản Doanh nghiệp (role='business') truy cập
    """
    serializer_class = BusinessEmployeeSerializer
    
    # Áp dụng Custom Permission tại đây, DRF sẽ tự động chặn request ngay từ cửa
    permission_classes = [IsBusinessRole]

    def get_queryset(self):
        # Chỉ lấy danh sách nhân viên thuộc về doanh nghiệp đang gọi API
        return BusinessEmployee.objects.filter(business=self.request.user)

    def perform_create(self, serializer):
        # Code giờ đây rất sạch, chỉ còn tập trung vào việc lưu data
        # Hệ thống tự động gắn doanh nghiệp tạo ra nhân viên này là user đang đăng nhập
        serializer.save(business=self.request.user)