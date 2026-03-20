from rest_framework import permissions

class IsBusinessRole(permissions.BasePermission):
    """
    Custom permission: Chỉ cho phép các user có role là 'business' truy cập.
    """
    # Câu thông báo lỗi trả về khi user không có quyền
    message = "Chỉ tài khoản Doanh nghiệp mới có quyền thực hiện hành động này."

    def has_permission(self, request, view):
        # Yêu cầu: 
        # 1. Có request.user (tồn tại user)
        # 2. User đã xác thực (đăng nhập)
        # 3. Role của user phải là 'business'
        return bool(
            request.user and 
            request.user.is_authenticated and 
            getattr(request.user, 'role', None) == 'business'
        )