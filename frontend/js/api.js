// Cấu hình URL của Backend Django
const BASE_URL = 'http://127.0.0.1:8000/api';

// Hàm xử lý khi bấm nút Đăng Nhập
async function loginUser() {
    const usernameInput = document.getElementById('username').value;
    const passwordInput = document.getElementById('password').value;
    const errorMsg = document.getElementById('error-msg');

    // Ẩn thông báo lỗi trước khi gửi
    errorMsg.style.display = 'none';

    try {
        // Gửi dữ liệu tới API login của Django
        const response = await fetch(`${BASE_URL}/users/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: usernameInput,
                password: passwordInput
            })
        });

        if (response.ok) {
            const data = await response.json();
            // Đăng nhập thành công, Backend sẽ trả về Token (giấy thông hành)
            // Lưu Token này vào bộ nhớ trình duyệt để dùng cho các trang sau
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            
            alert('Đăng nhập thành công!');
            // Chuyển hướng sang trang danh sách sản phẩm
            window.location.href = 'products.html'; 
        } else {
            // Sai tài khoản/mật khẩu
            errorMsg.style.display = 'block';
        }
    } catch (error) {
        console.error('Lỗi kết nối:', error);
        alert('Không thể kết nối đến máy chủ. Vui lòng kiểm tra lại Backend.');
    }
}