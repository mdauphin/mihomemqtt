import socket
import binascii
import struct
import json
import paho.mqtt.client as mqtt
import syslog
 
MULTICAST_PORT = 9898
SERVER_PORT = 4321
 
MULTICAST_ADDRESS = '224.0.0.50'
SOCKET_BUFSIZE = 1024
 
MQTT_SERVER = "localhost"
MQTT_PORT = 1883
 
PATH_FMT = "xiaomi/{model}/{sid}/{prop}" # short_id or sid ?
 
 
def prepare_socket():
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
 
    sock.bind(("0.0.0.0", MULTICAST_PORT))
 
    mreq = struct.pack("=4sl", socket.inet_aton(MULTICAST_ADDRESS),
                       socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_BUFSIZE)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
 
    return sock
 
def prepare_mqtt():
    client = mqtt.Client()
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
 
    return client
 
LAST_TOKEN = None
 
def push_data(client, model, sid, cmd, data):
    if cmd == u"heartbeat":
        return
    for key, value in data.items():
        path = PATH_FMT.format(model=model,
                               sid=sid,
                               cmd=cmd,
                               prop=key)
        syslog.syslog(syslog.LOG_DEBUG,path)
        client.publish(path, payload=value)
 
    #elif cmd == "heartbeat":
    #    pass
 
def handle_incoming_data(client, payload):
    global LAST_TOKEN
    #print("incoming", payload)
    syslog.syslog(syslog.LOG_DEBUG, str(payload))
    if 'data' in payload:
        #print("push_data", payload['data'])
        push_data(client,
                  payload['model'],
                  payload['sid'],
                  payload['cmd'],
                  json.loads(payload["data"]))
 
    if "token" in payload:
        LAST_TOKEN = payload['token']
 
if __name__ == "__main__":
    sock = prepare_socket()
    client = prepare_mqtt()    
    syslog.syslog('Processing started')

    while True:
        data, addr = sock.recvfrom(SOCKET_BUFSIZE) # buffer size is 1024 bytes
        try:
            payload = json.loads(data.decode("utf-8"))
            handle_incoming_data(client, payload)
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,"{}:{}".format(data,e))
            print("Can't handle message %r (%r)" % (data, e))
