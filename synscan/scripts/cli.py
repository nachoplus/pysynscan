#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# pysynscan
# Copyright (c) July 2020 Nacho Mas

import click
import os

#GOTO
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--wait', type=bool, help='Wait until finished (default False)', default=False)
@click.argument('azimuth',type=float)
@click.argument('altitude',type=float)
def goto(host, port,azimuth,altitude,wait):
    """Do a GOTO to a target azimuth/altitude"""
    import synscan
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    smc.goto(azimuth,altitude,syncronous=wait)


#TRACK
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.argument('azimuth_speed',type=float)
@click.argument('altitude_speed',type=float)
def track(host, port, azimuth_speed, altitude_speed):
    """Move at desired speed (degrees per second)"""
    import synscan
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    smc.track(azimuth_speed,altitude_speed)

#STOP
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--wait', type=bool, help='Wait until finished', default=True)
def stop(host, port,wait):
    """Stop Motors"""
    import synscan
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    smc.axis_stop_motion(1,syncronous=wait)
    smc.axis_stop_motion(2,syncronous=wait)


#SHOW
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--seconds', type=float, help='Show every N seconds (default 1s)', default=1)
def watch(host, port,seconds):
    """Watch values"""
    import synscan
    import json
    import time
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    while True:
        response=smc.update_current_values(logaxis=3)
        t = time.localtime()
        response['TIME']=time.strftime("%H:%M:%S", t)
        print(json.dumps(
            response,
            sort_keys=False,
            indent=4,
            separators=(',', ': ')
        ))
        time.sleep(seconds)

#SYNCRONIZE
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.argument('azimuth',type=float)
@click.argument('altitude',type=float)
def syncronize(host, port,azimuth,altitude):
    """Syncronize actual position with the azimuth/altitude provided"""
    import synscan
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    smc.set_pos(azimuth,altitude)

#Set On/off auxiliary switch
@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--seconds', type=float, help='Seconds to automatic deactivation', default=0)
@click.argument('on',type=bool)
def switch(host, port, on,seconds):
    """Activate/Deactivate mount auxiliary switch. ON must be bool (1 or 0)"""
    import synscan
    import time
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    smc=synscan.motors(UDP_IP,UDP_PORT)
    if seconds>0:
        smc.set_switch(on)
        time.sleep(seconds)
        smc.set_switch(not on)
    else:
        smc.set_switch(on)

