from django.db import models
from users.models import CustomUser
from products.models import Product

# --- 1. BẢNG GIỎ HÀNG (Lưu tạm chưa mua) ---
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# --- 2. BẢNG ĐƠN HÀNG (Đã chốt mua) ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Hoàn tất'),
        ('cancelled', 'Hủy'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Nhân viên tư vấn được gắn vào đơn này (có thể do Admin phân công)
    consultant = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='consulted_orders')
    
    created_at = models.DateTimeField(auto_now_add=True)
    # File hợp đồng PDF sẽ được upload lên đây
    contract_file = models.FileField(upload_to='contracts/', null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    # Lưu lại giá tại thời điểm mua (đề phòng sau này admin đổi giá sản phẩm)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)