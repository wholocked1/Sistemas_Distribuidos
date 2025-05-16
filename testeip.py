#Codigo verificar ip que está usando:

import socket
import psutil

def get_current_connections():
    """
    Retrieves and prints the IP and port addresses of current network connections.
    """
    connections = psutil.net_connections()
    for conn in connections:
      if conn.status == psutil.CONN_ESTABLISHED:
        try:
          local_address = conn.laddr
          remote_address = conn.raddr
          print(f"Local IP: {local_address.ip}, Local Port: {local_address.port}, Remote IP: {remote_address.ip}, Remote Port: {remote_address.port}")
        except AttributeError:
          print("Connection details not available.")

get_current_connections()