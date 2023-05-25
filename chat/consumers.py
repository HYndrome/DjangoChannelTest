import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        if message_type == 'chat':
            message = text_data_json['message']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
        elif message_type == 'draw':
            x = text_data_json['x']
            y = text_data_json['y']
            color = text_data_json['color']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'draw_message',
                    'x': x,
                    'y': y,
                    'color': color,
                }
            )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))

    async def draw_message(self, event):
        x = event['x']
        y = event['y']
        color = event['color']

        await self.send(text_data=json.dumps({
            'type': 'draw',
            'x': x,
            'y': y,
            'color': color,
        }))