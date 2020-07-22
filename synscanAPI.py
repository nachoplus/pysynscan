import os
import logging
import synscancomm

UDP_IP = os.getenv("SYNSCAN_UDP_IP","192.168.4.1")
UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",11880)



class synscanMount(synscancomm.synscanComm):
    def __init__(self):
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:synscanAPI %(message)s',
            level=logging.DEBUG
            )
        super(synscanMount, self).__init__(udp_ip=UDP_IP,udp_port=UDP_PORT)
        self.params=self.get_parameters()
        logging.debug(f'{self.params}')

    def get_parameters(self):
        parameterDict={ 'countsPerRevolution':'a',
                        'TimerInterrup':'b',
                        'StepPeriod':'i',
                        'MotorBoardVersion':'e'
                        }
        return self.get_values(parameterDict)

    def get_current_values(self):
        parameterDict={ 'GotoTarget':'h',
                        'Position':'j',
                        'Status':'f'
                        }

        return self.get_values(parameterDict)

    def get_values(self,parameterDict):
        params=dict()
        for parameter,cmd in parameterDict.items():
            params[parameter]=dict()
            for axis in range(1,3):
                params[parameter][axis]=self.send_cmd(cmd,axis)
        return params

    def get_axis_pos(self,axis):
        response=self.send_cmd('j',axis)
        return response

    def set_goto_target(self,axis,target):
        response=self.send_cmd('S',axis,target)
        return response

    def start_motion(self,axis):
        response=self.send_cmd('J',axis)
        return response


if __name__ == '__main__':
    smc=synscanMount()
    logging.info(f"Get AXIS=1 pos")
    print(smc.get_axis_pos(1))
    logging.info(f"Get AXIS=2 pos")
    print(smc.get_axis_pos(2))
    print(smc.get_current_values())
    #print(smc.set_goto_target(1,102310))
    #print(smc.start_motion(1))
