from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

# Import từ các app khác một cách ngắn gọn, chính xác
from products.models import Product

# Import các file nội bộ của app orders
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer

# =======================================================================
# PHẦN 1: API DÀNH CHO KHÁCH HÀNG (CÁ NHÂN / DOANH NGHIỆP)
# =======================================================================

# 1. API Xem giỏ hàng của chính mình
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Tự động tìm hoặc tạo giỏ hàng cho user đang đăng nhập
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

# 2. API Thêm sản phẩm vào giỏ hàng
class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        # Tìm sản phẩm, nếu không có trả về lỗi 404
        product = get_object_or_404(Product, id=product_id)
        
        # Tìm giỏ hàng của user đang đăng nhập (chưa có thì tự tạo)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Thêm sản phẩm vào giỏ, nếu có rồi thì cộng dồn số lượng
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += int(quantity)
            cart_item.save()
            
        return Response({"message": "Đã thêm vào giỏ hàng thành công!"}, status=status.HTTP_200_OK)

# 3. API Chuyển Giỏ hàng thành Đơn hàng (Checkout)
class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()
        
        if not cart or cart.items.count() == 0:
            return Response({"error": "Giỏ hàng đang trống"}, status=status.HTTP_400_BAD_REQUEST)

        # 3.1 Tạo đơn hàng mới
        order = Order.objects.create(user=user, status='pending', total_price=0)
        total_price = 0

        # 3.2 Chuyển item từ Giỏ sang Đơn
        for item in cart.items.all():
            price = item.product.price if item.product.price else 0
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity, price=price
            )
            total_price += price * item.quantity

        # 3.3 Cập nhật tổng tiền đơn hàng và xóa giỏ hàng
        order.total_price = total_price
        order.save()
        cart.items.all().delete()

        return Response({"message": "Lên đơn thành công!", "order_id": order.id}, status=status.HTTP_201_CREATED)


# =======================================================================
# PHẦN 2: API DÀNH CHO NỘI BỘ (SUPER ADMIN / ADMIN / STAFF)
# =======================================================================

# 1. Tạo chốt chặn: Chỉ cho phép Admin, Super Admin hoặc Staff
class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'super_admin', 'staff']
        )

# 2. API Lấy danh sách toàn bộ đơn hàng (Sắp xếp mới nhất lên đầu)
class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]

# 3. API Xem chi tiết, Duyệt đơn và Upload file PDF Hợp đồng
class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]
    # Khai báo parser để backend hiểu được file PDF gửi lên từ Dashboard
    parser_classes = (MultiPartParser, FormParser)


# 4. API Lấy danh sách đơn hàng của chính User đang đăng nhập
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ lấy các đơn hàng thuộc về user này, xếp mới nhất lên đầu
        return Order.objects.filter(user=self.request.user).order_by('-created_at')