# import sys
# import paho.mqtt.client as mqtt
# import json
# import os
# import django

# # Configurer Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
# django.setup()

# from supervisor.models.node import Node
# from supervisor.models.data import Data
# from django.utils import timezone

# USER = "fire-detction-app@ttn"
# PASSWORD = "NNSXS.DVAOEHXTPMPFFOT57RT76FBXLIGB6YIAQRB6JEY.7CDXFNCQ4AYSGSMBQU6PE3LXRIHGCRYWS3UK4745OZZWL6NJBCLA"
# PUBLIC_TLS_ADDRESS = "eu1.cloud.thethings.network"
# PUBLIC_TLS_ADDRESS_PORT = 8883
# DEVICE_ID = "eui-70b3d57ed0066fcf"
# ALL_DEVICES = True

# QOS = 2

# DEBUG = True

# def stop(client):
#     client.disconnect()
#     print("\nExit")
#     sys.exit(0)

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("\nConnected successfully to MQTT broker")
#     else:
#         print("\nFailed to connect, return code = " + str(rc))

# def on_message(client, userdata, message):
#     parsed_json = json.loads(message.payload)

#     # Extract and print temperature, humidity, gaz, pressure, detection and rssi
#     decoded_payload = parsed_json["uplink_message"]["decoded_payload"]
#     temperature = decoded_payload.get("temperature", "N/A")
#     humidity = decoded_payload.get("humidity", "N/A")
#     gaz = decoded_payload.get("gaz", "N/A")
#     pressure = decoded_payload.get("pressur", "N/A")
#     detection = decoded_payload.get("detection", "N/A")
#     rssi = parsed_json["uplink_message"]["rx_metadata"][0].get("rssi", "N/A")

#     print(f"Temperature: {temperature}°C")
#     print(f"Humidity: {humidity}%")
#     print(f"Gas: {gaz} ppm")
#     print(f"Pressure: {pressure} hPa")
#     print(f"Detection: {detection}")
#     print(f"RSSI: {rssi} dBm")

#     # Enregistrer les données dans la base de données
#     device_id = parsed_json["end_device_ids"]["device_id"]
#     try:
#         node = Node.objects.get(reference=device_id)
#         data = Data(
#             temperature=temperature,
#             humidity=humidity,
#             pressur=pressure,
#             gaz=gaz,
#             detection=detection,
#             published_date=timezone.now(),
#             node=node
#         )
#         data.save()
#         print("Data saved successfully")
#     except Node.DoesNotExist:
#         print(f"No Node found with reference: {device_id}")

# def on_subscribe(client, userdata, mid, granted_qos):
#     print("\nSubscribed with message id (mid) = " + str(mid) + " and QoS = " + str(granted_qos))

# def on_disconnect(client, userdata, rc):
#     print("\nDisconnected with result code = " + str(rc))

# print("Create new mqtt client instance")
# mqttc = mqtt.Client()

# print("Assign callback functions")
# mqttc.on_connect = on_connect
# mqttc.on_subscribe = on_subscribe
# mqttc.on_message = on_message
# mqttc.on_disconnect = on_disconnect

# mqttc.username_pw_set(USER, PASSWORD)
# mqttc.tls_set()  # default certification authority of the system

# print("Connecting to broker: " + PUBLIC_TLS_ADDRESS + ":" + str(PUBLIC_TLS_ADDRESS_PORT))
# mqttc.connect(PUBLIC_TLS_ADDRESS, PUBLIC_TLS_ADDRESS_PORT, 60)

# if ALL_DEVICES:
#     print("Subscribe to all topics (#) with QoS = " + str(QOS))
#     mqttc.subscribe("#", QOS)
# elif len(DEVICE_ID) != 0:
#     topic = "v3/" + USER + "/devices/" + DEVICE_ID + "/up"
#     print("Subscribe to topic " + topic + " with QoS = " + str(QOS))
#     mqttc.subscribe(topic, QOS)
# else:
#     print("Can not subscribe to any topic")
#     stop(mqttc)

# print("And run forever")
# try:
#     run = True
#     while run:
#         mqttc.loop(10)  # seconds timeout / blocking time
#         print(".", end="", flush=True)  # feedback to the user that something is actually happening
# except KeyboardInterrupt:
#     stop(mqttc)
