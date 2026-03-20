from django.urls import path
from .views import ProductListView, ProductDetailView, NewsListView, NewsDetailView

urlpatterns = [
    # API Sản phẩm
    path('', ProductListView.as_view(), name='api_product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='api_product_detail'),
    
    # API Tin tức
    path('news/', NewsListView.as_view(), name='api_news_list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='api_news_detail'),
]