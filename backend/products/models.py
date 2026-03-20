from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    target = models.CharField(max_length=20, choices=(('individual', 'Cá nhân'), ('business', 'Doanh nghiệp')))

    def __str__(self):
        return f"{self.name} ({self.get_target_display()})"

class Product(models.Model):
    TERM_CHOICES = (
        ('6_months', '6 Tháng'),
        ('1_year', '1 Năm'),
        ('2_years', '2 Năm'),
        ('3_years', '3 Năm'),
        ('custom', 'Custom'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    
    # Giá: Cho phép bỏ trống (null) để hiển thị chữ "Liên hệ tư vấn" trên giao diện
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True) 
    
    provider_name = models.CharField(max_length=255) # Đơn vị cung cấp
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Bảng phụ để 1 sản phẩm có thể up được nhiều ảnh
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')



# =======================================================================
# BẢNG DỮ LIỆU TIN TỨC (NEWS)
# =======================================================================
class News(models.Model):
    title = models.CharField(max_length=255) # Tiêu đề bài viết
    content = models.TextField() # Nội dung chi tiết
    image = models.ImageField(upload_to='news_images/', null=True, blank=True) # Ảnh minh họa
    is_active = models.BooleanField(default=True) # Trạng thái Ẩn/Hiện
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title