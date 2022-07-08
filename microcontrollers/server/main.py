"""
Source code of the "Microgames" server microcontroller.
"""
from typing import Tuple, List, Optional, Iterator
import socket

import network

from events import Event, decode_event


DEBUG = True

UART_BAUDRATE = 38400
ACCESS_POINT_SSID = "microgrames-server-1"
ACCESS_POINT_PASSWORD = "microgrames-top"
ACCESS_POINT_AUTHMODE = network.AUTH_WPA_WPA2_PSK
SERVER_IP = "192.168.0.1"
SOCKET_PORT = 7777


def run():
    print("Program started.")

    print("Configuring access point...")
    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    ap.config(essid=ACCESS_POINT_SSID)
    ap.config(password=ACCESS_POINT_PASSWORD)
    ap.config(authmode=ACCESS_POINT_AUTHMODE)
    ap.ifconfig(("192.168.0.1", "255.255.255.0", "192.168.0.1", "8.8.8.8"))
    ap.active(True)
    print("Access point configured and activated.")

    ifconf = ap.ifconfig()
    print("Access point configuration:")
    print("  - IP: %s", ifconf[0])
    print("  - Subnet mask: %s", ifconf[1])
    print("  - Gateway: %s", ifconf[2])
    print("  - DNS: %s", ifconf[3])
    ip_address = ifconf[0]

    print("Configuring server socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_address, SOCKET_PORT))
    print("Server socket configured. Listening on %s:%d", ip_address, SOCKET_PORT)

    clients_events_parser = ClientsEventsParser()
    while True:
        try:
            data, address = sock.recvfrom(256) 
        except KeyboardInterrupt:
            break
        
        clients_events_parser.chunk_added(address, data)
        for client, event in clients_events_parser.parse_events():
            print("Event from {}:\n{}\n-----------------".format(client, event))

    sock.close()
    print("Server socket closed.")

    ap.active(False)
    print("Access point deactivated.")


Address = Tuple[str, int]


class ClientsEventsParser:
    def __init__(self):
        self.clients_data_to_parse = {}

    def chunk_added(self, address: Address, data: bytes):
        if address not in self.clients_data_to_parse:
            self.clients_data_to_parse[address] = data
        self.clients_data_to_parse[address] += data

    def parse_events(self) -> Iterator[Tuple[Address, List[Event]]]:
        for client_address, data in self.clients_data_to_parse.items():
            client_events = []

            while data:
                event, data = parse_event_from_client_data(data)
                if event:
                    client_address.append(event)
                else:
                    break

            self.clients_data_to_parse[client_address] = data
            yield client_address, client_events


# Parses first event from data.
#
# Data is represented in the form of bytes, where
# each event should be in format: ^<event_id_byte><event_data_bytes>$
# However, due to data transmission issues, data can be split into chunks.
# For example: "00 fc ^ 03 fc $ ce ^ 10" will be parsed
# as event with id 3 with 1 byte of data 0xFC and all the
# remaining data will be returned as the second argument.
def parse_event_from_client_data(data: bytes) -> Tuple[Optional[Event], bytes]:
    event_prefix_i = data.find(b"^")

    if event_prefix_i == -1:
        # Prefix is not found, so data is useless
        return None, b""
    
    # Remove bytes before prefix to
    # 1) Avoid finding postfix before prefix
    # 2) Remove useless bytes
    data = data[event_prefix_i:]

    event_postfix_i = data.find(b"$")
    if event_postfix_i == -1:
        return None, data
    
    rem = data[event_postfix_i+1:]
    event = decode_event(data[event_prefix_i+1:event_postfix_i])

    return event, rem


if __name__ == "__main__":
    run()
