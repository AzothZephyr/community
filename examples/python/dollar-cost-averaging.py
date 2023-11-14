import threading
import websocket
import time
import hmac
import hashlib
import base64
import json
from market_data_pb2 import AggMessage
import ssl
from trade_pb2 import NewOrder, Side, OrderType, TimeInForce
import random
import struct

class WebSocketClient:
    def __init__(self):
        self.__data = []
        self.__ws = websocket.WebSocketApp("wss://147.28.171.25/md/tops",
                                           on_message=self.__on_message,
                                           on_error=self.__on_error,
                                           on_close=self.__on_close)
        self.__ws.on_open = self.__on_open
        self.__ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def __on_message(self, ws, message):
        decoded_message = AggMessage()
        decoded_message.ParseFromString(message)
        # print(decoded_message)

    def __on_error(self, ws, error):
        print(error)

    def __on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def __on_open(self, ws):
        self.__send_command('auth', [self.__get_auth()])
        self.__wait_for_account()
        self.__wait_for_symbol('AAPL')

        # Start a thread for sending heartbeat
        threading.Thread(target=self.__send_heartbeat, daemon=True).start()

    def __get_auth(self):
        secret_key = api_key  # Replace this with your actual secret key
        timestamp = int(time.time() * 1000)
        message = b"cube.xyz" + timestamp.to_bytes(8, byteorder='little')
        signature = hmac.new(secret_key.encode(), message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    def __send_command(self, command, params):
        data = json.dumps({"command": command, "params": params})
        self.__ws.send(data)

    def __wait_for_account(self):
        # Implement logic to wait for account information
        pass

    def __wait_for_symbol(self, symbol):
        # Implement logic to wait for symbol information
        pass

    def __send_heartbeat(self):
        while True:
            request_id = random.randint(0, 2**64 - 1)
            current_time = int(time.time())
            heartbeat_message = struct.pack("<QQ", request_id, current_time)
            self.__ws.send(heartbeat_message)
            print("sent heartbeat:" + heartbeat_message)
            time.sleep(29)

if __name__ == "__main__":
    WebSocketClient()