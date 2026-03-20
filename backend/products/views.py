from rest_framework import generics, permissions

# Import models và serializers nội bộ của app products
from .models import Product, News
from .serializers import ProductSerializer, NewsSerializer

# =======================================================================
# API DÀNH CHO SẢN PHẨM (GÓI BẢO HIỂM)
# =======================================================================

class ProductListView(generics.ListAPIView):
    """
    API Lấy danh sách gói bảo hiểm.
    - Ai cũng có thể xem (AllowAny).
    - Chỉ lấy sản phẩm đang hoạt động (is_active=True), xếp mới nhất lên đầu.
    - Hỗ trợ lọc theo đối tượng: ?target=individual hoặc ?target=business
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        
        # Bắt tham số 'target' từ URL để lọc danh sách
        target = self.request.query_params.get('target', None)
        if target:
            queryset = queryset.filter(category__target=target)
            
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    """
    API Lấy chi tiết 1 gói bảo hiểm cụ thể.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# =======================================================================
# API DÀNH CHO TIN TỨC (NEWS)
# =======================================================================

class NewsListView(generics.ListAPIView):
    """
    API Lấy danh sách tin tức hiển thị ra trang chủ.
    - Ai cũng có thể xem (AllowAny).
    - Chỉ lấy tin đang hoạt động (is_active=True), xếp mới nhất lên đầu.
    """
    queryset = News.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

class NewsDetailView(generics.RetrieveAPIView):
    """
    API Xem chi tiết 1 bài tin tức cụ thể.
    """
    queryset = News.objects.filter(is_active=True)
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]