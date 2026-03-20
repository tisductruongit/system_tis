from rest_framework import serializers
from .models import Category, Product, ProductImage

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'name', 'description', 'term', 'price', 'provider_name', 'is_active', 'images']

    # Hàm can thiệp vào dữ liệu trước khi trả về cho người dùng
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Nếu chưa đăng nhập HOẶC quyền không phải là admin/super_admin thì xóa field provider_name
        if request and hasattr(request, 'user'):
            if not request.user.is_authenticated or request.user.role not in ['admin', 'super_admin']:
                data.pop('provider_name', None)
        else:
            data.pop('provider_name', None)
            
        return data
    
# =======================================================================
# SERIALIZER CHO TIN TỨC
# =======================================================================
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'image', 'is_active', 'created_at']