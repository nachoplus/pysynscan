import time
import synscan

smc=synscan.motors()

#Set actual position az=0 alt=0 
smc.set_pos(0,0)

#define a grid and walk over his points
for az in range(0,180,30):
    for alt in range(0,90,30):
        smc.goto(az,alt,synchronous=True)    #Goto and wait to finish
        smc.set_switch(True)                #Activate camera with the integrate switch
        time.sleep(2)
        smc.set_switch(False)
