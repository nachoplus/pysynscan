# -*- coding: iso-8859-15 -*-
#
# pysynscan
# Copyright (c) July 2020 Nacho Mas


import socket
import logging
import os
import select
import threading



UDP_IP = os.getenv("SYNSCAN_UDP_IP","192.168.4.1")
UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",11880)

LOGGING_LEVEL=os.getenv("SYNSCAN_LOGGING_LEVEL",logging.INFO)

class comm:
    '''
    UDP Comunication module.
    Virtual. Used as base class. All members are protected
    '''
    def __init__(self,udp_ip=UDP_IP,udp_port=UDP_PORT):
        ''' Init the UDP socket '''
       
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:synscanComm %(message)s',
            level=LOGGING_LEVEL
            )
        logging.info(f"UDP target IP: {udp_ip}")
        logging.info(f"UDP target port: {udp_port}")
        self._sock = socket.socket(socket.AF_INET, # Internet
        socket.SOCK_DGRAM) # UDP
        self._sock.setblocking(0)
        self.udp_ip=udp_ip
        self.udp_port=udp_port
        self.commOK=False
        self.lock= threading.Lock()

    
    def _send_raw_cmd(self,cmd,timeout_in_seconds=2):
        '''Low level send command function ''' 
        with self.lock:   
            self._sock.sendto(cmd,(self.udp_ip,self.udp_port))
            ready = select.select([self._sock], [], [], timeout_in_seconds)
            if ready[0]:
                self.commOK=True
                response,(fromhost,fromport) = self._sock.recvfrom(1024)
                logging.debug(f"response: {response} host:{fromhost} port:{fromport}" )
            else:
                self.commOK=False
                logging.debug(f"Socket timeout. {timeout_in_seconds}s without response" )
                raise(NameError('SynscanSocketTimeoutError'))
                response = False        
        return response

    def _send_cmd(self,cmd,axis,data=None,ndigits=6):
        '''Command function '''
        if data is None:
           ndigits=0
        msg=bytes(f':{cmd}{axis}{self._int2hex(data,ndigits)}\r','utf-8')
        logging.debug(f'sending cmd:{msg}')
        raw_response=self._send_raw_cmd(msg)

        #If everything is OK first char must be '=' (code 61)
        if raw_response[0]==61:
            response=self._hex2int(raw_response[1:-1])
            return response

        #If something goes wrong first char must be '!' (code 33)
        if raw_response[0]==33:
            ErrorDict={0:'UnknownCommand',1:'CommandLengthError',2:'MotorNotStopped',3:'InvalidCharacter',
                       4:'NotInitialized',5:'DriverSleeping',7:'PECTrainingIsRunning',8:'NoValidPECdata'}
            errorNumber=self._hex2int(raw_response[1:-1])
            if errorNumber not in [0,1,2,3,4,5,7,8]:
                logging.warning(f'Unknown Error {raw_response}')
                raise(NameError('CMDUnknowError'))
                return False                    
            errorStr=ErrorDict[errorNumber]
            logging.warning(f'CMD:{msg} Error:{errorStr} {raw_response}')
            raise(NameError(errorStr))
            return False
        #Catch the rest
        else:
            logging.warning(f'Unknown Error {raw_response}')
            raise(NameError('CMDUnknowError'))
            return False





    def _int2hex(self,data,ndigits=6):
        ''' Convert data prior to send to the motors following 
            Synscan Motor Protocol rules
   
        * 24 bits Data Sample: for HEX number 0x123456, in the data segment of
          a command or response, it is sent/received in this order: "5" "6" "3" "4" "1" "2".
        * 16 bits Data Sample: For HEX number 0x1234, in the data segment of a command or 
          response, it is sent/received in this order: "3" "4" "1" "2". 
        * 8 bits Data Sample: For HEX number 0x12, in the data segment of a command or
          response, it is sent/received in this order: "1" "2".
        '''

        assert (ndigits in [0,1,2,4,6]), "ndigits must be one of [0,2,4,6]"
        if ndigits==6:
            strData=f'{data:06X}'
        if ndigits==4:
            strData=f'{data:04X}'
        if ndigits==2:
            strData=f'{data:02X}'
        if ndigits==1:
            strData=f'{data:01X}'
        if ndigits==0:
            strData=f''
        length=len(strData)
        strHEX=''
        for i in range(length,0,-2):
            strHEX=strHEX+f'{strData[i-2:i]}'
        logging.debug(f'{data}(decimal) => {strData}(hex) => {strHEX}(synscan hex)')
        return strHEX
        
    def _hex2int(self,data):
        ''' Convert data recived from motors following 
            Synscan Motor Protocol rules
   
        * 24 bits Data Sample: for HEX number 0x123456, in the data segment of
          a command or response, it is sent/received in this order: "5" "6" "3" "4" "1" "2".
        * 16 bits Data Sample: For HEX number 0x1234, in the data segment of a command or 
          response, it is sent/received in this order: "3" "4" "1" "2". 
        * 8 bits Data Sample: For HEX number 0x12, in the data segment of a command or
          response, it is sent/received in this order: "1" "2".
        '''
        strData=data.decode("utf-8") 
        length=len(strData)
        assert (length<=6), f"Max allow value is FFFFFF. Actual={strData}"
        #Special cases
        #Some commands dont return data
        if length==0:
            return ''
        #Status msg only return 12 bits (1.5bytes or 3 hex digits)
        if length==3:
            logging.debug(f'3bytes response. Not converting to init. Returning as it as string')        
            return strData
        #General case. Returned msd has 1,2,3 bytes (2,4 or 6 hex digits)
        logging.debug(f'Converting {strData} to a integer')
        strHEX=''
        for i in range(length,0,-2):
            strHEX=strHEX+f'{strData[i-2:i]}'
        v=int(strHEX,16)
        logging.debug(f'{strData}(synscan hex) => {strHEX}(hex) => {v}(decimal)')
        return v

    def _test_comm(self):
        '''Control msg to check comms'''
        MESSAGE = b":F3\r"
        logging.info(f"Testing comms. Asking if initialized..")
        response=self._send_raw_cmd(MESSAGE)
        
        if response == b'=\r':
            logging.info(f"Mount initialized. Connection OK" )
        else:
            logging.info(f"Mount not initialized. Connection FAIL" )

if __name__ == '__main__':
    smc=comm()
    smc._int2hex(smc._hex2int(b'1FCA89'))
    smc._int2hex(smc._hex2int(b'5F3A'),4)
    smc._int2hex(smc._hex2int(b'B8'),2)


