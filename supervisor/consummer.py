import json
import paho.mqtt.client         as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.models.node     import Node
from supervisor.models.data     import Data
from django.utils               import timezone

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

    async def disconnect(self, close_code):
        self.client.loop_stop()

    def on_message(self, client, userdata, message):
        parsed_json = json.loads(message.payload)
        decoded_payload = parsed_json["uplink_message"]["decoded_payload"]
        temperature = decoded_payload.get("temperature", "N/A")
        humidity = decoded_payload.get("humidity", "N/A")
        gaz = decoded_payload.get("gaz", "N/A")
        pressure = decoded_payload.get("pressur", "N/A")
        detection = decoded_payload.get("detection", "N/A")
        rssi = parsed_json["uplink_message"]["rx_metadata"][0].get("rssi", "N/A")
        device_id = parsed_json["end_device_ids"]["device_id"]

        try:
            node = Node.objects.get(reference=device_id)
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
            print("Data saved successfully")
        except Node.DoesNotExist:
            print(f"No Node found with reference: {device_id}")
