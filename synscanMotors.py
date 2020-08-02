# -*- coding: iso-8859-15 -*-
#
# pysynscan
# Copyright (c) July 2020 Nacho Mas


import os
import logging
import synscanComm
import time

UDP_IP = os.getenv("SYNSCAN_UDP_IP","192.168.4.1")
UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",11880)

LOGGING_LEVEL=os.getenv("SYNSCAN_LOGGING_LEVEL",logging.INFO)

class synscanMotors(synscanComm.synscanComm):
    '''
    Implementation of all motor commands and logic
    following the document:
    https://inter-static.skywatcher.com/downloads/skywatcher_motor_controller_command_set.pdf

    IMPORTANT NOTES(based on the above doc):

    In the motor controller, there is a hardware timer T1 that is used to generate stepping pulse
    for stepper motor or reference position for servomotor. The input clock’s frequency of the timer,
    plus the preset value of this timer, determine the slewing speed of the motors. 

    ** For GOTO mode, the motor controller will take care of T1 automatically. But motion mode has to be set to tracking=False**

    When T1 generates an interrupt, it might:
        * Drive the motor to move 1 step (1 micro-step or 1 encoder tick) for low speed slewing.
        * Drive the motor to move up to 32 steps for high speed slewing. This method applies to motor
          controller firmware version 2.xx. For motor controller with firmware 3.xx or above, the motor
          controller always drive the motor controller 1 steps/interrupt.


    Typical session:
        * Check whether the motor is in full stop status. If not, stop it. 
        * Set the motion mode. 
        * Set the parameters, for example, destination or preset value of T1. 
        * Set the "Start" command. 
        * For a GOTO slewing, check the motor status to confirm that the motor stops (Generally means arriving the destination. ).
          For a Speed mode slewing, send "Stop" command to end the session. 

        Generally, the motor controller returns to "Speed Mode" when the motor stops automatically. 
    '''
    def __init__(self):
        '''Init UDP comunication '''      
        logging.basicConfig(
            format='%(asctime)s %(levelname)s:synscanMotor: %(message)s',
            level=LOGGING_LEVEL
            )
        super(synscanMotors, self).__init__(udp_ip=UDP_IP,udp_port=UDP_PORT)
        self.init()
        self.update_current_values()


    def init(self):
        '''Get main motor parameters. Retry if comm fails'''
        retrySec=2
        try:
            self.params=self.get_parameters()
        except NameError as error:
            logging.warning(error)
            logging.warning(f'Retriying in {retrySec}..')
            time.sleep(retrySec)
            self.init()

    def degrees2counts(self,axis,degrees):
        '''Return position or speed in counts for a given deg or deg/seconds value'''
        CPR=self.params[axis]['countsPerRevolution']
        value=degrees*CPR/360
        return value

    def counts2degrees(self,axis,counts):
        '''Return position or speed in degrees for a given counts or counts/seconds value'''
        CPR=self.params[axis]['countsPerRevolution']
        value=counts*360/CPR
        return value

    def degreesPerSecond2T1preset(self,axis,degreesPerSecond):
        countsPerSecond=self.degrees2counts(axis,degreesPerSecond)
        TMR_Freq=self.params[axis]['TimerInterruptFreq']
        if abs(countsPerSecond) <=0:
            T1preset=TMR_Freq
        else:
            T1preset=TMR_Freq/abs(countsPerSecond)
        return T1preset


    def get_values(self,parameterDict):
        '''
        Send all cmd in the parameterDict for both axis and return
        a dictionary with the values.
        Used by get_parameters and update_current_values functions
        '''
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

    def get_parameters(self):
        '''
        Get main motor parameters.
        Some of this parameters are needed for all calculations 
        so they have to be available to the rest of the code
        '''
        parameterDict={ 'countsPerRevolution':'a',
                        'TimerInterruptFreq':'b',
                        'StepPeriod':'i',
                        'MotorBoardVersion':'e',
                        'HighSpeedRatio':'g',
                        }
        try:
            params=self.get_values(parameterDict)
        except NameError as error:
            logging.warning(error)
            raise(NameError('getParametersError'))
            return {}
        logging.info(f'MOUNT PARAMETERS: {params}')
        return params

    def update_current_values(self,logaxis=2):
        '''Get current status and values'''
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
                #Position values are offseting by 0x800000
                params[axis][parameter]=params[axis][parameter]-0x800000
        for axis in range(1,3):
            params[axis]['Status']=self.decode_status(params[axis]['Status'])
        self.values=params
        if logaxis==3:
            logging.info(f'Actual values {params}')
        if logaxis in [1,2]:
            logging.info(f'AXIS{logaxis} {params[logaxis]}')
        return params

    def decode_status(self,hexstring):
        ''' Decode Status msg.
        Status msg is 12bits long (3 HEX digits). 
        
        HEX digit1 bits:
        B0: 1=Tracking,0=Goto
        B1: 1=CCW,0=CW
        B2: 1=Fast,0=Slow

        HEX digit2 bits:
        B0: 1=Running,0=Stopped
        B1: 1=Blocked,0=Normal

        HEX digit3 bits:
        B0: 0 = Not Init,1 = Init done
        B1: 1 = Level switch on

        '''
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


    def set_motion_mode(self,axis,Tracking,CW=True,fastSpeed=False):
        '''Set Motion Mode.

        Channel will always be set to Tracking Mode after stopped

        1byte msg (2 HEX digits)

        HEX Digit 1 bits:
        B0: 0=Goto, 1=Tracking
        B1: 0=Slow, 1=Fast  (T)
            0=Fast, 1=Slow  (G)
        B2: 0=S/F, 1=Medium
        B3: 1x SlowGoto

        HEX Digit 2 bits:  
        B0: 0=CW,1=CCW
        B1: 0=Noth,1=South
        B2: 0=Normal Goto,1=Coarse Goto
        '''
        if not Tracking:
            if fastSpeed:
                speedBit=0
            else:
                speedBit=1
        else:
            if fastSpeed:
                speedBit=1
            else:
                speedBit=0
        if Tracking:
            value=16
        else:
            value=0
        value=value+speedBit*32+CW
        #Send as two HEX digits
        logging.info(f'AXIS{axis}: Setting Motion Mode: {value} HEX:{value:02X}')
        response=self.send_cmd('G',axis,value,ndigits=2) 
        return response        

    def set_T1_preset(self,axis,value):
        '''Set step period for tracking speed'''
        logging.info(f'AXIS{axis}: Setting step_period to: {value} counts per seconds')
        response=self.send_cmd('I',axis,value)
        return response

    def get_axis_posCounts(self,axis):
        '''Get actual postion in StepsCounts.'''
        #Position values are offseting by 0x800000
        response=self.send_cmd('j',axis)-0x800000
        return response

    def set_goto_targetCounts(self,axis,targetCounts):
        '''GoTo Target value in StepsCounts. Motors has to be stopped'''
        logging.info(f'AXIS{axis}: Setting goto target to {targetCounts} counts')
        #Position values are offseting by 0x800000
        response=self.send_cmd('S',axis,targetCounts+0x800000)
        return response

    def wait2stop(self,axis):    
        logging.info(f'AXIS{axis}: Waitting to stop.')
        self.update_current_values()
        while not self.values[axis]['Status']['Stopped']:
            time.sleep(2)
            self.update_current_values()
        logging.info(f'AXIS{axis}: Stopped')

    def set_posCounts(self,axis,counts):
        '''Syncronize position Counts.'''
        logging.info(f'AXIS{axis}: Syncronizing actual position to {counts} counts')
        #Position values are offseting by 0x800000
        response=self.send_cmd('E',axis,counts+0x800000)
        return response


    #HIGH LEVEL API (arguments in degrees)
    def set_switch(self,on):
        '''Switch on/off auxiliary switch'''
        if on:
            value=1
        else:
            value=0
        logging.info(f'Auxiliary swtich: {on}')
        response=self.send_cmd('O',value)
        return response

    def get_axis_pos(self,axis):
        '''Get actual position in Degrees.'''
        counts=self.get_axis_posCounts(axis)
        return self.counts2degrees(counts)

    def set_axis_pos(self,axis,degrees):
        '''Syncronize position Degrees.'''
        logging.info(f'AXIS{axis}: Syncronizing actual position to {degrees} degrees')
        counts=self.degrees2counts(axis,degrees)
        response=self.set_posCounts(axis,int(counts))

    def set_pos(self,alpha,beta):
        self.set_axis_pos(1,alpha)
        self.set_axis_pos(1,beta)

    def set_goto_target(self,axis,targetDegrees):
        '''GoTo Target value in Degrees. Motors has to be stopped'''
        logging.info(f'AXIS{axis}: Setting goto target to {targetDegrees} degrees')
        posCounts=self.degrees2counts(axis,targetDegrees)
        response=self.set_goto_targetCounts(axis,int(posCounts))
        return response

    def goto_axis(self,axis,targetDegrees):
        self.stop_motion(axis)
        self.set_motion_mode(axis,False,False,False)
        self.set_goto_target(axis,targetDegrees)
        self.start_motion(axis)

    def set_speed(self,axis,degreesPerSecond):
        '''Set the tracking speed in degreesPerSecond'''
        logging.info(f'AXIS{axis}: Setting speed to:{degreesPerSecond} degrees per second')
        if degreesPerSecond!=0:
            response=self.set_T1_preset(axis,int(self.degreesPerSecond2T1preset(axis,abs(degreesPerSecond))))
        else:
            response=self.stop_motion(axis)
        return response

    def track_axis(self,axis,speed):
        #Check if we need to stop axis
        self.update_current_values(axis)
        stopped=self.values[axis]['Status']['Stopped']
        CW=not self.values[axis]['Status']['CCW']
        tracking=self.values[axis]['Status']['Tracking']
        if not stopped:
            if not tracking or (CW and (speed <0)) or (not CW and (speed >0)):
                logging.info(f'TRACK asked to change dir or mode tracking:{tracking} CW:{CW} speed:{speed}')
                self.stop_motion(axis,syncronous=True)
                self.set_motion_mode(axis,True,(speed <0),False)
                self.set_speed(axis,speed)
                self.start_motion(axis)
                return 
            else:
                self.set_speed(axis,speed)
                return 
        else:
            self.set_speed(axis,speed)
            self.start_motion(axis)
            return

    def start_motion(self,axis):
        '''Start Goto'''
        response=self.send_cmd('J',axis)
        logging.info(f'AXIS{axis}: Starting motion')
        return response

    def stop_motion(self,axis,syncronous=True):
        '''Soft stop. If syncronous==True wait to finish'''
        logging.info(f'AXIS{axis}: Stopping')
        response=self.send_cmd('K',axis)
        if syncronous:
            self.wait2stop(axis)
        else:
            logging.info(f'AXIS{axis}: Ask to stop. In progress')
        return response

    def goto(self,alpha,beta,syncronous=True):
        '''GOTO. alpha,beta in degrees'''
        logging.info(f'GOTO axis1={alpha} axis2={beta} degrees')
        for axis in [1,2]:
            self.stop_motion(axis)
            self.set_motion_mode(axis,False,False,False)
        self.set_goto_target(1,alpha)
        self.set_goto_target(2,beta)
        for axis in [1,2]:
            self.start_motion(axis)
        if syncronous:
            for axis in [1,2]:
                self.wait2stop(axis)


    def track(self,alpha,beta):
        '''GOTO. alpha,beta in degrees per second'''
        logging.info(f'TRACK speeds axis1={alpha} axis2={beta} degrees per seconds')
        self.track_axis(1,alpha)
        self.track_axis(2,beta)

    def test_goto(self,axis=2,X=90):
        '''Test GOTO. X in degrees'''
        logging.info(f'AXIS{axis}: GOTO test')
        self.stop_motion(axis)
        self.set_motion_mode(axis,False,X,False)
        self.set_goto_target(axis,X)
        self.start_motion(axis)
        self.update_current_values(AXIS)
        while not self.values[axis]['Status']['Stopped']:
            time.sleep(2)
            self.update_current_values(AXIS)

    def test_slew(self,axis=1,speed=1):
        '''Test SLEW'''
        logging.info(f'AXIS{axis}: SLEW test')
        self.stop_motion(axis)
        self.set_motion_mode(axis,True,(speed>=0),True)
        self.set_speed(axis,speed)
        self.start_motion(axis)




if __name__ == '__main__':
    smc=synscanMotors()
    smc.set_pos(0,0)
    #AXIS to test
    AXIS=2
    
    #Test GOTO
    if False:
        smc.test_goto(axis=AXIS,X=45)
        smc.test_goto(axis=AXIS,X=0)
        exit(0)

    #Test SLEW
    if False:
        smc.test_slew(axis=AXIS,speed=.5)
        smc.wait2stop(AXIS)
        exit(0)

    #Two axes goto
    if True:
        smc.goto(5,15)
        smc.goto(0,0)
        exit(0)

    #Ramp tracking
    if False:
        for speed in range(0,50,1):
            time.sleep(.1)
            smc.track_axis(AXIS,speed/10)
        for speed in range(50,0,-1):
            time.sleep(.1)
            smc.track_axis(AXIS,speed/10)
        for speed in range(0,50,1):
            time.sleep(.1)
            smc.track_axis(AXIS,-speed/10)
        for speed in range(50,0,-1):
            time.sleep(.1)
            smc.track_axis(AXIS,-speed/10)

    #GOTO/TRACK interrupts
    if True:
        pass


