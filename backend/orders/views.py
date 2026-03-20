from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

# Import từ các app khác
from products.models import Product

# Import các file nội bộ của app orders
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer

# =======================================================================
# PHẦN 1: API DÀNH CHO KHÁCH HÀNG (CÁ NHÂN / DOANH NGHIỆP)
# =======================================================================

# 1. API Xem giỏ hàng của chính mình
class CartDetailView(generics.RetrieveAPIView):
    """Lấy thông tin giỏ hàng của User đang đăng nhập"""
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Tự động tìm hoặc tạo giỏ hàng cho user đang đăng nhập
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

# 2. API Thêm sản phẩm vào giỏ hàng
class AddToCartView(APIView):
    """Thêm gói bảo hiểm vào giỏ hàng"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        
        # Đảm bảo quantity luôn là số nguyên (chống lỗi crash khi client gửi chuỗi)
        try:
            quantity = int(request.data.get('quantity', 1))
        except ValueError:
            quantity = 1
        
        # Tìm sản phẩm, nếu không có trả về lỗi 404
        product = get_object_or_404(Product, id=product_id)
        
        # Tìm giỏ hàng của user đang đăng nhập (chưa có thì tự tạo)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Tối ưu logic: Nếu tạo mới thì gán luôn quantity, nếu đã có thì cộng dồn
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
            
        return Response({"message": "Đã thêm vào giỏ hàng thành công!"}, status=status.HTTP_200_OK)

# 3. API Chuyển Giỏ hàng thành Đơn hàng (Checkout)
class CheckoutView(APIView):
    """Thanh toán / Lên đơn hàng"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        # Tối ưu truy vấn CSDL: Dùng prefetch_related để tránh lỗi N+1 Query khi lặp qua các items
        cart = Cart.objects.prefetch_related('items__product').filter(user=user).first()
        
        if not cart or cart.items.count() == 0:
            return Response({"error": "Giỏ hàng đang trống"}, status=status.HTTP_400_BAD_REQUEST)

        # 3.1 Tạo đơn hàng mới (tổng tiền tạm thời bằng 0)
        order = Order.objects.create(user=user, status='pending', total_price=0)
        total_price = 0

        # 3.2 Chuyển item từ Giỏ sang Đơn
        for item in cart.items.all():
            price = item.product.price if item.product.price else 0
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, price=price
            )
            total_price += price * item.quantity

        # 3.3 Cập nhật tổng tiền đơn hàng và xóa trắng giỏ hàng
        order.total_price = total_price
        order.save()
        cart.items.all().delete()

        return Response(
            {"message": "Lên đơn thành công!", "order_id": order.id}, 
            status=status.HTTP_201_CREATED
        )


# =======================================================================
# PHẦN 2: API DÀNH CHO NỘI BỘ (SUPER ADMIN / ADMIN / STAFF)
# =======================================================================

# 1. Tạo chốt chặn: Chỉ cho phép Admin, Super Admin hoặc Staff
class IsAdminOrStaff(permissions.BasePermission):
    """Quyền truy cập dành riêng cho Ban quản trị"""
    message = "Bạn không có quyền thực hiện hành động này. Yêu cầu tài khoản Admin/Staff."
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', '') in ['admin', 'super_admin', 'staff']
        )

# 2. API Lấy danh sách toàn bộ đơn hàng
class AdminOrderListView(generics.ListAPIView):
    """Admin xem toàn bộ đơn hàng trong hệ thống"""
    # Dùng prefetch_related để tối ưu hiệu suất khi truy xuất thông tin user của order
    queryset = Order.objects.select_related('user').all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]

# 3. API Xem chi tiết, Duyệt đơn và Upload file PDF Hợp đồng
class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    """Admin xử lý đơn hàng cụ thể (Duyệt, upload PDF)"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]
    # Khai báo parser để backend hiểu được file PDF gửi lên từ Dashboard
    parser_classes = (MultiPartParser, FormParser)


# =======================================================================
# PHẦN 3: API LỊCH SỬ MUA HÀNG CỦA USER
# =======================================================================

# 1. API Lấy danh sách đơn hàng của chính User đang đăng nhập
class UserOrderListView(generics.ListAPIView):
    """Khách hàng xem lịch sử đơn hàng của chính mình"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy các đơn hàng thuộc về user này, xếp mới nhất lên đầu
        return Order.objects.filter(user=self.request.user).order_by('-created_at')