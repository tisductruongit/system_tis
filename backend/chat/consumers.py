# backend/chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models import ConsultationRequest, ChatMessage, User
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Lấy consultation_id từ URL (ws://.../ws/chat/<id>/)
        self.consultation_id = self.scope['url_route']['kwargs']['consultation_id']
        self.room_group_name = f'chat_{self.consultation_id}'

        # Tham gia vào room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Rời khỏi room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Nhận dữ liệu từ WebSocket (Client gửi lên)
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type in ['typing', 'stop_typing']:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_control',
                    'msg_type': msg_type,
                    'sender_id': data.get('sender_id')
                }
            )
            return

        message = data.get('message')
        # SỬA ĐỔI: Lấy thêm sender_name từ payload
        sender_id = data.get('sender_id')
        sender_name_payload = data.get('sender_name') 
        is_staff = data.get('is_staff', False)

        # Lưu tin nhắn và nhận lại object đã xử lý
        # Lưu tin nhắn vào Database
        saved_message = await self.save_message(message, sender_id, is_staff)

        # Kiểm tra nếu lưu thành công mới gửi đến Group
        if saved_message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': saved_message['message'],
                    # ... các thông tin khác
                }
            )
    # Xử lý sự kiện gửi tin nhắn văn bản xuống Client
# SỬA ĐỔI: Đảm bảo chat_message gửi đầy đủ data xuống client
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_name': event['sender_name'],
            'is_staff_reply': event['is_staff_reply'],
            'created_at': event['created_at'],
            'avatar': event['avatar'],
            'attachment_url': event.get('attachment_url'),
            'attachment_type': event.get('attachment_type'),
            'is_read': event.get('is_read')
        }))

    # Xử lý sự kiện gửi trạng thái (typing/stop_typing) xuống Client
    async def chat_control(self, event):
        await self.send(text_data=json.dumps({
            'type': event['msg_type'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, message, sender_id, is_staff, sender_name_payload):
        try:
            consultation = ConsultationRequest.objects.get(id=self.consultation_id)
        except ConsultationRequest.DoesNotExist:
            return None

        sender = None
        if sender_id:
            try:
                sender = User.objects.get(id=sender_id)
            except User.DoesNotExist:
                pass

        # Tạo bản ghi tin nhắn mới
        msg = ChatMessage.objects.create(
            consultation=consultation,
            sender=sender,
            message=message,
            is_staff_reply=is_staff
        )
        
        avatar_url = sender.avatar.url if sender and sender.avatar else None
        
        # SỬA ĐỔI: Ưu tiên tên từ User model, nếu không có thì dùng tên từ payload, cuối cùng là mặc định
        display_name = "Khách hàng"
        if sender:
            display_name = f"{sender.last_name} {sender.first_name}".strip() or sender.username
        elif sender_name_payload:
            display_name = sender_name_payload

        return {
            'message': msg.message,
            'sender_name': display_name,
            'is_staff_reply': msg.is_staff_reply,
            'created_at': msg.created_at.strftime('%H:%M'),
            'avatar': avatar_url,
            'attachment_url': None, # Hiện tại chưa xử lý gửi file qua WS
            'attachment_type': None,
            'is_read': False
        }