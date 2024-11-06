from channels.generic.websocket import AsyncWebsocketConsumer
import json
import jwt
from channels.db import database_sync_to_async
from django.conf import settings
from .models import User, ChatMessage  # Adjust imports based on your actual models

class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['query_string'].decode('utf-8').split('=')[1]  # Extract token from query params
        user, error = await self.get_user_from_token(token)
       
        if user:
            chat_with_user = self.scope['url_route']['kwargs']['id']
            user_ids = sorted([int(user.id), int(chat_with_user)])
            self.room_name = f'chat_{user_ids[0]}_{user_ids[1]}'
            
            # Add the user to the room
            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('id')
            user = User.objects.filter(pk=user_id, approval_status="approved").first()
            if user:
                return user, None
            else:
                return None, "User not found"
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data) 
        message = data['message']  
       
        receiver_id = data['receiver_id']
        sender_id = self.scope['user'].id 


        # Save the message to the database
        await self.save_message(sender_id, receiver_id, message)
        
        # Send the message to the room group with sender information
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender_id,
                "receiver": receiver_id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver=event['receiver']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "sender": sender,
            "receiver": receiver
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
