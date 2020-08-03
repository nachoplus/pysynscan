import synscan.synscanMotors as synscanMotors

def goto_test(az,alt):
    '''Goto Test function.'''
    smc=synscanMotors.synscanMotors()
    smc.set_pos(0,0)
    smc.goto(az,alt)
    smc.goto(0,0)

if __name__=='__main__':
    goto_test(30,30)
