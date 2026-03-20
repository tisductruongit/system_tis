from django.urls import path
from .views import CartDetailView, CheckoutView, AddToCartView, AdminOrderListView, AdminOrderDetailView, UserOrderListView

urlpatterns = [
    # Của Khách hàng
    path('cart/', CartDetailView.as_view(), name='api_cart_detail'),
    path('cart/add/', AddToCartView.as_view(), name='api_cart_add'),
    path('checkout/', CheckoutView.as_view(), name='api_checkout'),
    path('my-orders/', UserOrderListView.as_view(), name='api_user_orders'), # Thêm dòng này
    
    # Của Admin/Staff
    path('admin-orders/', AdminOrderListView.as_view(), name='api_admin_orders'),
    path('admin-orders/<int:pk>/', AdminOrderDetailView.as_view(), name='api_admin_order_detail'),
]