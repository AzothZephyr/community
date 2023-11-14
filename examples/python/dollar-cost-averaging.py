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
    def __init__(self, market_data_url, trade_url):
        self.__data = []
        self.__market_data_ws = websocket.WebSocketApp(market_data_url,
                                                       on_message=self.__on_market_data_message,
                                                       on_error=self.__on_error,
                                                       on_close=self.__on_close)
        self.__market_data_ws.on_open = self.__on_market_data_open

        self.__trade_ws = websocket.WebSocketApp(trade_url,
                                                 on_message=self.__on_trade_message,
                                                 on_error=self.__on_error,
                                                 on_close=self.__on_close)
        self.__trade_ws.on_open = self.__on_trade_open

        # Start threads for both connections
        threading.Thread(target=self.__market_data_ws.run_forever, daemon=True).start()
        threading.Thread(target=self.__trade_ws.run_forever, daemon=True).start()

    def __on_market_data_message(self, ws, message):
        decoded_message = AggMessage()
        decoded_message.ParseFromString(message)
        print("Market Data:", decoded_message)

    def __on_trade_message(self, ws, message):
        # Implement logic for handling trade messages
        print("Trade Data:", message)

    def __on_error(self, ws, error):
        print(error)

    def __on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def __on_market_data_open(self, ws):
        self.__send_market_data_command('auth', [self.__get_auth()])
        self.__wait_for_account()
        self.__wait_for_symbol('AAPL')

        # Start a thread for sending heartbeat to market data endpoint
        threading.Thread(target=self.__send_heartbeat, daemon=True, args=(self.__market_data_ws,)).start()

    def __on_trade_open(self, ws):
        # Implement logic for trade connection open
        # TODO: authenticate 
        
        # Start a thread for sending heartbeat to trade endpoint
        threading.Thread(target=self.__send_heartbeat, daemon=True, args=(self.__trade_ws,)).start()
        pass

    def __get_auth(self):
        secret_key = api_key  # Replace this with your actual secret key
        timestamp = int(time.time() * 1000)
        message = b"cube.xyz" + timestamp.to_bytes(8, byteorder='little')
        signature = hmac.new(secret_key.encode(), message, hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    def __send_market_data_command(self, command, params):
        # data = json.dumps({"command": command, "params": params})
        # self.__market_data_ws.send(data)
        pass

    def __send_trade_command(self, command, params):
        # data = json.dumps({"command": command, "params": params})
        # self.__trade_ws.send(data)
        pass

    def __wait_for_account(self):
        # Implement logic to wait for account information
        pass

    def __wait_for_symbol(self, symbol):
        # Implement logic to wait for symbol information
        pass

    def __send_heartbeat(self, ws):
        while True:
            request_id = random.randint(0, 2**64 - 1)
            current_time = int(time.time())
            heartbeat_message = struct.pack("<QQ", request_id, current_time)
            ws.send(heartbeat_message)
            time.sleep(29)

    def create_market_order(self, market_id, amount):
        precision = 8  # Replace with the actual precision of the asset

        # Convert the amount to an integer with the appropriate precision
        quantity_int = int(amount * 10**precision)

        # Implement logic to create a market order
        order = NewOrder()
        order.market_id = market_id
        order.quantity = quantity_int
        order.side = Side.BID  # or Side.ASK for sell
        order.order_type = OrderType.MARKET_LIMIT
        order.time_in_force = TimeInForce.GOOD_FOR_SESSION # good until websockets session closes

        self.__send_trade_command('create_order', [order.SerializeToString()])


if __name__ == "__main__":
    market_data_url = "wss://staging.cube.exchange/md/tops"  # Replace with the actual market data URL
    trade_url = "wss://staging.cube.exchange/os"  # Replace with the actual trade URL
    
    # Replace these values with the actual market ID and amount
    # 100000 is marketid for tETH/tBTC
    market_id = 100000
    amount = 0.1

    # Specify the interval for creating market orders (in seconds)
    order_interval = 60
    
    # Specify the maximum amount
    max_amount = 1.0

    client = WebSocketClient(market_data_url, trade_url)

    while True:
        # Adjust the amount based on the maximum amount
        amount = min(amount, max_amount)
        client.create_market_order(market_id, amount)
        time.sleep(order_interval)
