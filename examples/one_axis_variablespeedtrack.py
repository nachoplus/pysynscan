import synscan
import time
'''One axis variable speed track example'''
smc=synscan.motors()

AXIS=2
#FORWARD
#RAMP UP
for speed in range(0,50,1):
    time.sleep(.1)
    smc.axis_track(AXIS,speed/10)
#RAMP DOWN
for speed in range(50,0,-1):
    time.sleep(.1)
    smc.axis_track(AXIS,speed/10)

#BACKWARDS
#RAMP UP
for speed in range(0,50,1):
    time.sleep(.1)
    smc.axis_track(AXIS,-speed/10)
#RAMP DOWN
for speed in range(50,0,-1):
    time.sleep(.1)
    smc.axis_track(AXIS,-speed/10)

