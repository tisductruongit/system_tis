from rest_framework import serializers
from .models import CustomUser, BusinessEmployee

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'phone', 'role', 'address', 'cccd', 'company_name', 'tax_code']

    def validate(self, data):
        role = data.get('role', 'individual')
        email = data.get('email', '')
        
        # Bắt buộc thông tin với Doanh nghiệp
        if role == 'business':
            if not data.get('company_name') or not data.get('tax_code'):
                raise serializers.ValidationError("Tài khoản Doanh nghiệp bắt buộc phải nhập Tên công ty và Mã số thuế.")
        
        # Phân quyền nội bộ
        if role in ['admin', 'super_admin', 'staff']:
            if not email.endswith('@tisbroker.com'):
                raise serializers.ValidationError("Tài khoản nội bộ bắt buộc sử dụng email đuôi @tisbroker.com.")
                
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # QUAN TRỌNG: Đã thêm is_staff và is_superuser vào đây
        fields = ['id', 'username', 'email', 'phone', 'role', 'address', 'cccd', 'company_name', 'tax_code', 'specialty', 'is_staff', 'is_superuser']
        read_only_fields = ['username', 'email', 'phone', 'role', 'is_staff', 'is_superuser']

class BusinessEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessEmployee
        fields = ['id', 'full_name', 'email_or_phone', 'address']

    def create(self, validated_data):
        business = self.context['request'].user
        return BusinessEmployee.objects.create(business=business, **validated_data)