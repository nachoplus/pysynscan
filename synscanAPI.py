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
        logging.info(f'MOUNT PARAMETERS: {self.params}')

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
        return params

    def get_current_values(self):
        parameterDict={ 'GotoTarget':'h',
                        'Position':'j',
                        'Status':'f'
                        }
        try:
            params=self.get_values(parameterDict)
        except NameError as error:
            logging.warning(error)
            return {}
        for parameter in ['GotoTarget','Position']:
            for axis in range(1,3):
                params[parameter][axis]=params[parameter][axis]-8388608
        return params

    def get_values(self,parameterDict):
        params=dict()
        for parameter,cmd in parameterDict.items():
            params[parameter]=dict()
            for axis in range(1,3):
                try:
                    params[parameter][axis]=self.send_cmd(cmd,axis)
                except NameError as error:
                    logging.warning(error)
                    raise(NameError('getValuesError'))
        return params

    def get_axis_pos(self,axis):
        response=self.send_cmd('j',axis)
        return response

    def set_goto_target(self,axis,target):
        response=self.send_cmd('S',axis,target+8388608)
        return response

    def start_motion(self,axis):
        response=self.send_cmd('J',axis)
        return response


if __name__ == '__main__':
    smc=synscanMount()
    smc.set_goto_target(2,80)
    smc.start_motion(2)
    while True:
        time.sleep(2)
        print(smc.get_current_values())
