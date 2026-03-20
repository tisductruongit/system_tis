from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class AIChatView(APIView):
    # Cho phép ai cũng có thể chat (kể cả chưa đăng nhập)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user_message = request.data.get('message', '')
        
        if not user_message:
            return Response({"error": "Vui lòng nhập câu hỏi."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # -------------------------------------------------------------
            # CẤU HÌNH KẾT NỐI TỚI API MODEL RIÊNG CỦA BẠN
            # -------------------------------------------------------------
            # Thay đổi base_url thành địa chỉ IP/Port của server AI của bạn
            # Ví dụ LM Studio thường chạy ở: http://localhost:1234/v1
            llm = ChatOpenAI(
                base_url="http://localhost:1234/v1", 
                api_key="not-needed", # Đa số model local không cần key
                model="local-model",  # Tên model tùy ý
                temperature=0.7
            )

            # Tạo ngữ cảnh (Prompt) cho AI đóng vai chuyên viên tư vấn
            messages = [
                SystemMessage(content="Bạn là trợ lý ảo AI chuyên nghiệp của công ty môi giới bảo hiểm TIS Broker. Hãy trả lời ngắn gọn, lịch sự và thân thiện bằng tiếng Việt."),
                HumanMessage(content=user_message)
            ]

            # Gọi Model xử lý
            ai_response = llm.invoke(messages)

            return Response({
                "reply": ai_response.content,
                "status": "success"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Bắt lỗi nếu server AI chưa bật hoặc sai đường dẫn
            return Response({
                "error": f"Lỗi kết nối AI: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)