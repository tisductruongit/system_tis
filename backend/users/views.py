from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserProfileSerializer

# API Đăng ký tài khoản
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Cho phép bất kỳ ai cũng có thể gọi API này

# API Xem và Cập nhật Profile
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated] # Bắt buộc phải đăng nhập (có token) mới được gọi

    def get_object(self):
        # Tự động lấy profile của chính người đang đăng nhập, không xem được của người khác
        return self.request.user


from rest_framework import serializers
from .models import BusinessEmployee
from .serializers import BusinessEmployeeSerializer

# API cho phép Doanh nghiệp xem danh sách và thêm nhân viên
class BusinessEmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = BusinessEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy danh sách nhân viên của chính doanh nghiệp đang đăng nhập
        return BusinessEmployee.objects.filter(business=self.request.user)

    def perform_create(self, serializer):
        # Chốt chặn bảo mật: Chỉ user có role 'business' mới được thêm
        if self.request.user.role != 'business':
            raise serializers.ValidationError({"error": "Chỉ tài khoản Doanh nghiệp mới có quyền thêm nhân viên."})
        serializer.save()