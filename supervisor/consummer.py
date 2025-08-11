import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.models.node import Node
from supervisor.models.data import Data
from django.utils import timezone
from asgiref.sync import async_to_sync
from .fwi import FWI
from supervisor.tasks import predict_single_fwi

class MQTTConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        # self.client.username_pw_set("fire-detection-test@ttn", "NNSXS.EDJB7U3WTZADJOA34ILAM7LZCKIS7NFRGU36G4Y.6C3Z3OKA7GK5K6SUVBCY5GQZGZOJDJIOWSTKQW4QNTNWAFI2RNBQ")
        self.client.username_pw_set("lorae5app2@ttn", "NNSXS.7SPGHIMTGOGDQCROYRSD67YPZL4P5PZQ3MQJRCY.QBM3MPQHNDZWHOBTDDEUVQT2EBHP6ECICHBEWRZWWCGPMUY2FAKA")
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
            rain            = decoded_payload.get("rain", 0)  # Add rain for DMC calculation
            rssi            = parsed_json["uplink_message"]["rx_metadata"][0].get("rssi", "N/A")
            device_id       = parsed_json["end_device_ids"]["device_id"]

            fwi = FWI() #fwi_biblio
            wind = fwi.calculate_wind(temperature, humidity, pressure)

            try:
                nodes = Node.objects.filter(reference=device_id)
                if nodes.exists():
                    for node in nodes:
                        try:
                            last_data = Data.objects.filter(node=node).latest('published_date')
                            ffmc_prev = last_data.ffmc if last_data else 85
                            dmc_prev = last_data.dmc if last_data else 6  # Add DMC previous value
                        except Data.DoesNotExist:
                            ffmc_prev = 85
                            dmc_prev = 6  # Default DMC value

                        # Calculate FFMC, DMC, ISI but NOT FWI
                        ffmc_value = fwi.FFMC(temperature, humidity, wind, rain, ffmc_prev)
                        dmc_value = fwi.DMC(temperature, humidity, rain, dmc_prev)
                        isi_value = fwi.ISI(wind, ffmc_value)
                        # ELIMINATED: fwi_value = fwi.FWI(isi_value)  # No traditional FWI calculation
                        
                        # Save data with calculated values but FWI will come from prediction
                        data = Data(
                            temperature=temperature,
                            humidity=humidity,
                            pressur=pressure,
                            gaz=gaz,
                            wind=wind,
                            ffmc=ffmc_value,
                            dmc=dmc_value,
                            isi=isi_value,
                            fwi=0,  # Will be updated by ML prediction
                            published_date=timezone.now(),
                            node=node
                        )
                        data.save()
                        
                        # Launch ML prediction task
                        try:
                            predict_single_fwi.delay(data.idData)
                            print(f"ML prediction task launched for data ID: {data.idData}")
                            
                            # Use the last predicted FWI from previous predictions
                            try:
                                last_prediction = Data.objects.filter(
                                    node=node, 
                                    fwi__gt=0  # Only get records where FWI was predicted
                                ).latest('published_date')
                                fwi_value = last_prediction.fwi
                            except Data.DoesNotExist:
                                fwi_value = 0  # No prediction available yet
                            
                            # Update node with predicted FWI
                            node.FWI = fwi_value
                            node.save()
                            
                        except Exception as prediction_error:
                            print(f"Error launching prediction task: {prediction_error}")
                            fwi_value = 0  # No prediction available
                            node.FWI = 0
                            node.save()
                            
                    print("Data saved successfully for all nodes")
                else:
                    print(f"No Node found with reference: {device_id}")
            except Exception as e:
                print(f"Error saving data: {e}")
                # Set fallback values in case of error
                fwi_value = 0
                dmc_value = 0
            finally:
                async_to_sync(self.send_message_to_websocket)({
                    'temperature': temperature,
                    'humidity': humidity,
                    'gaz': gaz,
                    'pressure': pressure,
                    'rssi': rssi,
                    'wind_speed': wind,
                    'fwi': fwi_value,  # This will now be the predicted FWI only
                    'dmc': dmc_value,  # DMC is still calculated
                    'device_id': device_id
                })
        else:
            print("Invalid message format: 'uplink_message' or 'decoded_payload' missing")

    async def send_message_to_websocket(self, data):
        await self.send(text_data=json.dumps({
            'message': 'MQTT data received',
            'data': data
        }))
"""import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from supervisor.models.node import Node
from supervisor.models.data import Data
from django.utils import timezone
from asgiref.sync import async_to_sync
from .fwi import FWI
from supervisor.tasks import predict_single_fwi

class MQTTConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        # self.client.username_pw_set("fire-detection-test@ttn", "NNSXS.EDJB7U3WTZADJOA34ILAM7LZCKIS7NFRGU36G4Y.6C3Z3OKA7GK5K6SUVBCY5GQZGZOJDJIOWSTKQW4QNTNWAFI2RNBQ")
        self.client.username_pw_set("lorae5app2@ttn", "NNSXS.7SPGHIMTGOGDQCROYRSD67YPZL4P5PZQ3MQJRCY.QBM3MPQHNDZWHOBTDDEUVQT2EBHP6ECICHBEWRZWWCGPMUY2FAKA")
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
            rain            = decoded_payload.get("rain", 0)  # Add rain for DMC calculation
            rssi            = parsed_json["uplink_message"]["rx_metadata"][0].get("rssi", "N/A")
            device_id       = parsed_json["end_device_ids"]["device_id"]

            fwi = FWI()
            wind = fwi.calculate_wind(temperature, humidity, pressure)

            try:
                nodes = Node.objects.filter(reference=device_id)
                if nodes.exists():
                    for node in nodes:
                        try:
                            last_data = Data.objects.filter(node=node).latest('published_date')
                            ffmc_prev = last_data.ffmc if last_data else 85
                            dmc_prev = last_data.dmc if last_data else 6  # Add DMC previous value
                        except Data.DoesNotExist:
                            ffmc_prev = 85
                            dmc_prev = 6  # Default DMC value

                        ffmc_value = fwi.FFMC(temperature, humidity, wind, rain, ffmc_prev)  # Use rain instead of 0
                        dmc_value = fwi.DMC(temperature, humidity, rain, dmc_prev)  # Add DMC calculation
                        isi_value = fwi.ISI(wind, ffmc_value)
                        fwi_value = fwi.FWI(isi_value)
                        
                        node.FWI = fwi_value
                        node.save()

                        data = Data(
                            temperature=temperature,
                            humidity=humidity,
                            pressur=pressure,
                            gaz=gaz,
                            wind=wind,
                            ffmc=ffmc_value,
                            dmc=dmc_value,  # Add DMC to data saving
                            isi=isi_value,
                            fwi=fwi_value,
                            published_date=timezone.now(),
                            node=node
                        )
                        data.save()
                        
                        try:
                            predict_single_fwi.delay(data.idData)
                            print(f"ML prediction task launched for data ID: {data.idData}")
                        except Exception as prediction_error:
                            print(f"Error launching prediction task: {prediction_error}")
                            
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
                    'rssi': rssi,
                    'wind_speed': wind,
                    'fwi': fwi_value, 
                    'dmc': dmc_value,  # Add DMC to websocket message
                    'device_id': device_id
                })
        else:
            print("Invalid message format: 'uplink_message' or 'decoded_payload' missing")

    async def send_message_to_websocket(self, data):
        await self.send(text_data=json.dumps({
            'message': 'MQTT data received',
            'data': data
        })) """