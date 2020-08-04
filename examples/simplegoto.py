import synscan

'''Goto example'''
smc=synscan.motors()
#Syncronize mount actual position to (0,0)
smc.set_pos(0,0)
#Move forward and wait to finish
smc.goto(30,30,syncronous=True)
#Return to original position and exit without wait
smc.goto(0,0,syncronous=False)

