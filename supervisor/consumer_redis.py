import json
from channels.generic.websocket import AsyncWebsocketConsumer

FRONT_GROUP = "fwi_front"

class FrontWSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(FRONT_GROUP, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(FRONT_GROUP, self.channel_name)

    async def fwi_message(self, event):  
        await self.send(text_data=event["text"])













'''import json
from channels.generic.websocket import AsyncWebsocketConsumer

FRONT_GROUP = "fwi_front"

class FrontWSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(FRONT_GROUP, self.channel_name)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(FRONT_GROUP, self.channel_name)

    async def fwi_message(self, event):
        await self.send(text_data=event["text"])'''
