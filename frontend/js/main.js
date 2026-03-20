const BASE_URL = 'http://127.0.0.1:8000/api';

// Chạy ngay khi trang vừa load xong
document.addEventListener("DOMContentLoaded", () => {
    checkLoginStatus();
    fetchProducts();
});

// Kiểm tra xem đã đăng nhập chưa
function checkLoginStatus() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert("Bạn chưa đăng nhập. Vui lòng đăng nhập để tiếp tục.");
        window.location.href = 'login.html';
    }
}

// Xử lý Đăng xuất
function logoutUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = 'login.html';
}

// Lấy danh sách sản phẩm từ API
async function fetchProducts() {
    const productListDiv = document.getElementById('product-list');
    
    try {
        const response = await fetch(`${BASE_URL}/products/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
                // Ở đây API danh sách sản phẩm cấu hình là AllowAny nên không cần nhét Token vào Header
                // Tuy nhiên, nếu muốn backend biết ai đang gọi để ẩn/hiện provider_name, ta gửi kèm token:
            }
        });

        // Thử gửi kèm token nếu có để Backend nhận diện quyền Admin
        const token = localStorage.getItem('access_token');
        const headers = { 'Content-Type': 'application/json' };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const authResponse = await fetch(`${BASE_URL}/products/`, {
            method: 'GET',
            headers: headers
        });

        if (authResponse.ok) {
            const products = await authResponse.json();
            productListDiv.innerHTML = ''; // Xóa chữ "Đang tải dữ liệu..."

            if (products.length === 0) {
                productListDiv.innerHTML = '<p>Hiện tại chưa có gói bảo hiểm nào.</p>';
                return;
            }

            // Vòng lặp vẽ từng sản phẩm ra HTML
            products.forEach(product => {
                // Kiểm tra xem backend có trả về provider_name không (bảo mật role)
                const providerHtml = product.provider_name 
                    ? `<span class="provider">Cung cấp bởi: ${product.provider_name}</span>` 
                    : '';
                
                // Hiển thị giá hoặc chữ "Liên hệ tư vấn"
                const priceHtml = product.price 
                    ? `${Number(product.price).toLocaleString('vi-VN')} VNĐ` 
                    : 'Liên hệ tư vấn';

                const cardHtml = `
                    <div class="product-card">
                        <h3>${product.name}</h3>
                        <p><strong>Loại:</strong> ${product.category_name || 'Chưa phân loại'}</p>
                        <p><strong>Thời hạn:</strong> ${product.term}</p>
                        <p>${product.description}</p>
                        <div class="price">${priceHtml}</div>
                        ${providerHtml}
                        <button class="btn-buy" onclick="addToCart(${product.id})">Thêm vào giỏ</button>
                    </div>
                `;
                productListDiv.innerHTML += cardHtml;
            });
        } else {
            productListDiv.innerHTML = '<p style="color:red;">Lỗi tải dữ liệu sản phẩm.</p>';
        }
    } catch (error) {
        console.error('Lỗi:', error);
        productListDiv.innerHTML = '<p style="color:red;">Không thể kết nối đến máy chủ Backend.</p>';
    }
}

// Hàm giả lập thêm vào giỏ hàng (sẽ viết API gọi thật ở bước sau)
function addToCart(productId) {
    alert(`Đã thêm sản phẩm ID ${productId} vào giỏ hàng!`);
}


async function addToCart(productId) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert("Vui lòng đăng nhập để mua hàng!");
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/orders/cart/add/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // Phải trình thẻ token để backend biết ai đang thêm
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        });

        if (response.ok) {
            alert("Đã thêm gói bảo hiểm vào giỏ hàng thành công!");
            // Tùy chọn: Chuyển thẳng người dùng sang trang Giỏ hàng
            // window.location.href = 'cart.html';
        } else {
            alert("Có lỗi xảy ra, vui lòng thử lại.");
        }
    } catch (error) {
        console.error('Lỗi kết nối:', error);
    }
}