import json
import paho.mqtt.client         as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.models.node     import Node
from supervisor.models.data     import Data
from django.utils               import timezone
from asgiref.sync               import async_to_sync


class MQTTConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.username_pw_set("fire-detction-app@ttn", "NNSXS.DVAOEHXTPMPFFOT57RT76FBXLIGB6YIAQRB6JEY.7CDXFNCQ4AYSGSMBQU6PE3LXRIHGCRYWS3UK4745OZZWL6NJBCLA")
        self.client.tls_set()
        self.client.connect("eu1.cloud.thethings.network", 8883, 60)
        self.client.subscribe("#", 2)
        self.client.loop_start()
        print("MQTT connection established successfully")

    async def disconnect(self, close_code):
        self.client.loop_stop()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                await self.process_data(data)
            except json.JSONDecodeError:
                print("Invalid JSON received")
        else:
            print("No text data received")

    async def process_data(self, data):
        await self.send(text_data=json.dumps({
            'message': 'Data received',
            'data': data
        }))

    def on_message(self, client, userdata, message):
        parsed_json = json.loads(message.payload)
        
        if 'uplink_message' in parsed_json and 'decoded_payload' in parsed_json['uplink_message']:
            decoded_payload = parsed_json["uplink_message"]["decoded_payload"]
            temperature     = decoded_payload.get("temperature", "N/A")
            humidity        = decoded_payload.get("humidity", "N/A")
            gaz             = decoded_payload.get("gaz", "N/A")
            pressure        = decoded_payload.get("pressur", "N/A")
            detection       = decoded_payload.get("detection", "N/A")
            rssi            = parsed_json["uplink_message"]["rx_metadata"][0].get("rssi", "N/A")
            device_id       = parsed_json["end_device_ids"]["device_id"]

            try:
                nodes = Node.objects.filter(reference=device_id)
                if nodes.exists():
                    for node in nodes:
                        data = Data(
                            temperature=temperature,
                            humidity=humidity,
                            pressur=pressure,
                            gaz=gaz,
                            detection=detection,
                            published_date=timezone.now(),
                            node=node
                        )
                        data.save()
                    print("Data saved successfully for all nodes")
                else:
                    print(f"No Node found with reference: {device_id}")
            except Exception as e:
                print(f"Error saving data: {e}")
            finally:
                async_to_sync(self.send_message_to_websocket)({
                    'temperature': temperature,
                    'humidity': humidity,
                    'gaz': gaz,
                    'pressure': pressure,
                    'detection': detection,
                    'rssi': rssi,
                    'device_id': device_id
                })
        else:
            print("Invalid message format: 'uplink_message' or 'decoded_payload' missing")

    async def send_message_to_websocket(self, data):
        await self.send(text_data=json.dumps({
            'message': 'MQTT data received',
            'data': data
        }))
