from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('individual', 'Cá nhân'),
        ('business', 'Doanh nghiệp'),
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='individual')
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # --- Dành cho khách hàng Cá nhân ---
    cccd = models.CharField(max_length=20, null=True, blank=True)
    
    # --- Dành cho khách hàng Doanh nghiệp ---
    company_name = models.CharField(max_length=255, null=True, blank=True)
    tax_code = models.CharField(max_length=50, null=True, blank=True)

    # --- Dành cho Staff nội bộ TIS ---
    SPECIALTY_CHOICES = (
        ('property', 'Tài sản'),
        ('health', 'Sức khỏe'),
        ('vehicle', 'Xe'),
        ('marine', 'Hàng hải'),
    )
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.username or self.email

# Bảng phụ lưu danh sách nhân viên của doanh nghiệp mua bảo hiểm
class BusinessEmployee(models.Model):
    business = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employees')
    full_name = models.CharField(max_length=255)
    email_or_phone = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.business.company_name}"