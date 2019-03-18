import socket
import fcntl
import struct
 
class IPAddress():
#    def __init__(self):
#        print("Initalize IPAddress")
 
    def get_interface_ipaddress(self, network):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', network[:15])
        )[20:24])
#ethernet eth0  wifi wlan0
    def get_ipaddress(self, network='wlan0'):
        return self.get_interface_ipaddress(network)
