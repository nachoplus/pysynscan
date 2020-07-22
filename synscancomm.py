import socket
import logging
import os
import select

UDP_IP = os.getenv("SYNSCAN_UDP_IP","192.168.4.1")
UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",11880)


class synscanComm:
    def __init__(self,udp_ip=UDP_IP,udp_port=UDP_PORT):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:synscanComm %(message)s',
            level=logging.DEBUG
            )
        logging.info(f"UDP target IP: {udp_ip}")
        logging.info(f"UDP target port: {udp_port}")
        self.sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP
        self.sock.setblocking(0)
        self.udp_ip=udp_ip
        self.udp_port=udp_port
        self.commOK=False
        self.test_comm()
    
    def send_raw_cmd(self,cmd,timeout_in_seconds=2):
        logging.debug(f"Sending cmd:{cmd}")
        self.sock.sendto(cmd,(self.udp_ip,self.udp_port))
        ready = select.select([self.sock], [], [], timeout_in_seconds)
        if ready[0]:
            self.commOK=True
            response,(fromhost,fromport) = self.sock.recvfrom(1024)
            logging.debug(f"response: {response} host:{fromhost} port:{fromport}" )
        else:
            self.commOK=False
            response = False
            logging.debug(f"Socket timeout. {timeout_in_seconds}s without response" )
        return response

    def send_cmd(self,cmd,axis,data=None):
        if data is None:
            msg=bytes(f':{cmd}{axis}\r','utf-8')
        else:
            msg=bytes(f':{cmd}{axis}{data}\r','utf-8')
        response=self.send_raw_cmd(msg)
        return response

    def int2hex(self,data):
        pass

    def hex2int(self,data):
        pass

    def test_comm(self):
        MESSAGE = b":F3\r"
        logging.info(f"Testing comms. Asking if initialized..")
        response=self.send_raw_cmd(MESSAGE)
        
        if response == b'=\r':
            logging.info(f"Mount initialized. Connection OK" )
        else:
            logging.info(f"Mount not initialized. Connection FAIL" )

if __name__ == '__main__':
    smc=synscanComm()

