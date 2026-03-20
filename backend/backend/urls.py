from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings # Thêm dòng này
from django.conf.urls.static import static # Thêm dòng này
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


schema_view = get_schema_view(
   openapi.Info(
      title="TIS Insurance API",
      default_version='v1',
      description="Tài liệu API cho Hệ thống bán bảo hiểm trực tuyến",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # Thêm dòng này để nối API Chatbot
    path('api/chat/', include('chatbot.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
    
]

# Thêm 2 dòng này vào cuối cùng để hệ thống cho phép tải file PDF/Ảnh về máy
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)