let activeConsultationId = null;
let chatPollingInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    // Bảo vệ Route: Chỉ User đăng nhập mới được vào trang này
    if (!getAccessToken()) {
        window.location.href = '../login.html';
        return;
    }
    loadConsultations();
});

// 1. Tải danh sách các yêu cầu tư vấn của User
async function loadConsultations() {
    const listContainer = document.getElementById('ticket-list');
    try {
        const response = await fetchAPI('/consultations/', 'GET');
        
        if (!response || response.length === 0) {
            listContainer.innerHTML = `
                <div class="p-4 text-center text-muted">
                    <p>Bạn chưa có yêu cầu tư vấn nào.</p>
                    <a href="../products.html" class="btn btn-sm btn-outline-danger">Xem sản phẩm</a>
                </div>`;
            return;
        }

        listContainer.innerHTML = response.map(ticket => `
            <div class="chat-ticket ${activeConsultationId === ticket.id ? 'active' : ''}" 
                 onclick="openChat(${ticket.id}, '${ticket.status}')">
                <div class="d-flex justify-content-between mb-1">
                    <strong class="text-dark">Yêu cầu #${ticket.id}</strong>
                    <span class="badge ${ticket.status === 'new' ? 'bg-warning' : 'bg-success'} text-white" style="font-size: 0.6rem;">
                        ${ticket.status === 'new' ? 'Chờ xử lý' : 'Đang hỗ trợ'}
                    </span>
                </div>
                <div class="small text-muted text-truncate">${ticket.note || 'Tư vấn sản phẩm'}</div>
            </div>
        `).join('');

    } catch (e) {
        listContainer.innerHTML = `<div class="p-3 text-danger text-center">Lỗi tải dữ liệu!</div>`;
    }
}

// 2. Mở một phiên Chat
window.openChat = function(consultationId, status) {
    activeConsultationId = consultationId;
    
    // UI Update
    document.getElementById('chat-title').innerText = `Phiên tư vấn #${consultationId}`;
    document.getElementById('chat-status').innerText = status === 'new' ? 'Chuyên viên đang chuẩn bị phản hồi...' : 'Chuyên viên đang hỗ trợ';
    document.getElementById('chat-form').style.display = 'flex';
    
    // Highlight sidebar
    document.querySelectorAll('.chat-ticket').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active');

    // Tải tin nhắn và thiết lập Polling (Làm mới mỗi 3 giây)
    loadMessages();
    if (chatPollingInterval) clearInterval(chatPollingInterval);
    chatPollingInterval = setInterval(loadMessages, 3000);
}

// 3. Tải tin nhắn của phiên chat hiện tại
async function loadMessages() {
    if (!activeConsultationId) return;
    
    const chatBox = document.getElementById('chat-box');
    
    try {
        const messages = await fetchAPI(`/consultations/${activeConsultationId}/messages/`, 'GET');
        
        if (messages.length === 0) {
            chatBox.innerHTML = `<div class="text-center text-muted mt-4">Bắt đầu cuộc trò chuyện. Chuyên viên sẽ trả lời bạn sớm nhất.</div>`;
            return;
        }

        // Check xem có cần cuộn xuống đáy không (trước khi render lại)
        const isScrolledToBottom = chatBox.scrollHeight - chatBox.clientHeight <= chatBox.scrollTop + 50;

        chatBox.innerHTML = messages.map(msg => {
            const isUser = !msg.is_staff_reply;
            const time = new Date(msg.created_at).toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'});
            
            return `
                <div class="d-flex flex-column">
                    <div class="msg-bubble ${isUser ? 'msg-user' : 'msg-staff'} shadow-sm">
                        ${msg.message || '[Tệp đính kèm]'}
                    </div>
                    <small class="text-muted ${isUser ? 'text-end' : 'text-start'} mb-3" style="font-size: 0.65rem; margin-top: -10px; padding: 0 5px;">
                        ${isUser ? 'Bạn' : 'TIS Broker'} • ${time}
                    </small>
                </div>
            `;
        }).join('');

        // Cuộn xuống dòng tin nhắn mới nhất
        if (isScrolledToBottom) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (e) {
        console.error("Lỗi tải tin nhắn");
    }
}

// 4. Gửi tin nhắn
window.sendMessage = async function(e) {
    e.preventDefault();
    if (!activeConsultationId) return;

    const input = document.getElementById('msg-input');
    const text = input.value.trim();
    if (!text) return;

    // Tạm vô hiệu hóa ô input để tránh gửi 2 lần
    input.value = '';
    input.disabled = true;

    try {
        // Render tạm tin nhắn lên màn hình cho mượt (Optimistic UI)
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += `
            <div class="d-flex flex-column">
                <div class="msg-bubble msg-user shadow-sm opacity-50">${text}</div>
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        // Gọi API gửi tin
        await fetchAPI(`/consultations/${activeConsultationId}/messages/`, 'POST', { message: text });
        
        // Tải lại để lấy status chuẩn từ server
        loadMessages();
    } catch (e) {
        alert("Lỗi không thể gửi tin nhắn!");
    } finally {
        input.disabled = false;
        input.focus();
    }
}