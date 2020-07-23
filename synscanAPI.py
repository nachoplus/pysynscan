import os
import logging
import synscancomm
import time

UDP_IP = os.getenv("SYNSCAN_UDP_IP","192.168.4.1")
UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",11880)



class synscanMount(synscancomm.synscanComm):
    def __init__(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:synscanAPI %(message)s',
            level=logging.INFO
            )
        super(synscanMount, self).__init__(udp_ip=UDP_IP,udp_port=UDP_PORT)
        self.init()


    def init(self):
        retrySec=2
        try:
            self.params=self.get_parameters()
        except NameError as error:
            logging.warning(error)
            logging.warning(f'Retriying in {retrySec}..')
            time.sleep(retrySec)
            self.init()


    def get_parameters(self):
        parameterDict={ 'countsPerRevolution':'a',
                        'TimerInterrup':'b',
                        'StepPeriod':'i',
                        'MotorBoardVersion':'e'
                        }
        try:
            params=self.get_values(parameterDict)
        except NameError as error:
            logging.warning(error)
            raise(NameError('getParametersError'))
            return {}
        logging.info(f'MOUNT PARAMETERS: {params}')
        return params

    def get_current_values(self):
        parameterDict={ 'GotoTarget':'h',
                        'Position':'j',
                        'StepPeriod':'i',
                        'Status':'f'
                        }
        try:
            params=self.get_values(parameterDict)
        except NameError as error:
            logging.warning(error)
            return {}
        for parameter in ['GotoTarget','Position']:
            for axis in range(1,3):
                params[parameter][axis]=params[parameter][axis]-0x800000
        for axis in range(1,3):
            params['Status'][axis]=self.decode_status(params['Status'][axis])
        return params

    def decode_status(self,hexstring):
        A=int(hexstring[0],16)
        B=int(hexstring[1],16)
        C=int(hexstring[2],16)
        logging.debug(f'Decode status {hexstring} A:{A} B:{B} C:{C}')
        status=dict()
        status['Tracking']=bool(A & 0x01)
        status['CCW']=bool((A & 0x02) >> 1)
        status['FastSpeed']=bool((A & 0x04) >> 2)
        status['Stopped']=not(B & 0x01)
        status['Blocked']=bool((B & 0x02) >> 1)
        status['InitDone']=not(C & 0x01)
        status['LevelSwitchOn']=bool((B & 0x02) >> 1)
        return status


    def get_values(self,parameterDict):
        params=dict()
        for axis in range(1,3):
            params[axis]=dict()
            for parameter,cmd in parameterDict.items():
                try:
                    params[axis][parameter]=self.send_cmd(cmd,axis)
                except NameError as error:
                    logging.warning(error)
                    raise(NameError('getValuesError'))
        return params

    def set_motion_mode(self,axis,Tracking,fastSpeed,CW):
        if Tracking:
            if fastSpeed:
                speedBit=0x0
            else:
                speedBit=0x1
        else:
            if fastSpeed:
                speedBit=0x1
            else:
                speedBit=0x0
        value = (Tracking & 0x01) | (speedBit << 1) | ((CW & 0x01) <<7) 
        response=self.send_cmd('G',axis,value,ndigits=2)
        logging.info(f'AXIS{axis}:Setting Motion Mode: {value}')
        return response        

    def set_step_period(self,axis,value):
        response=self.send_cmd('I',axis,value)
        logging.info(f'AXIS{axis}:Setting step_period to: {value}')
        return response

    def get_axis_pos(self,axis):
        response=self.send_cmd('j',axis)
        return response

    def set_goto_target(self,axis,target):
        response=self.send_cmd('S',axis,target+0x800000)
        logging.info(f'AXIS{axis}:Setting goto target to {value}')
        return response

    def start_motion(self,axis):
        response=self.send_cmd('J',axis)
        logging.info(f'AXIS{axis}:Start motion to {value}')
        return response

    def stop_motion(self,axis):
        response=self.send_cmd('K',axis)
        return response


if __name__ == '__main__':
    smc=synscanMount()
    smc.stop_motion(3)
    AXIS=1
    smc.set_goto_target(AXIS,0)
    smc.set_motion_mode(AXIS,1,0,0)
    #smc.set_step_period(2,2000)
    smc.get_parameters()
    print(smc.get_current_values())
    smc.start_motion(AXIS)
    while True:
        time.sleep(2)
        print(smc.get_current_values())
