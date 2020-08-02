#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#
# pysynscan
# Copyright (c) July 2020 Nacho Mas

import click
import os

@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--azimuth', type=float, help='Azimuth (degrees)', default=0)
@click.option('--altitude', type=float, help='Altitude (degrees)', default=0)
@click.option('--sync', type=bool, help='Wait until finished', default=True)
def goto(host, port,azimuth,altitude,sync):
    """Do a GOTO to a desired azimuth/altitude"""
    import synscan.synscanMotors as synscanMotors
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    #click.echo("%s %u %s %u" % (host,port,parent_host,parent_port))
    smc=synscanMotors.synscanMotors(UDP_IP,UDP_PORT)
    smc.goto(azimuth,altitude,syncronous=sync)

@click.command()
@click.option('--host', type=str, help='Synscan mount IP address', default='192.168.4.1')
@click.option('--port', type=int, help='Synscan mount port', default=11880)
@click.option('--azSpeed', type=float, help='Azimuth speed (degrees per second)', default=0)
@click.option('--altSpeed', type=float, help='Altitude speed (degrees per second)', default=0)
def track(host, port,azSpeed,altSpeed):
    """Move at desired speed (degrees per second)"""
    import synscan.synscanMotors as synscanMotors
    UDP_IP = os.getenv("SYNSCAN_UDP_IP",host)
    UDP_PORT = os.getenv("SYNSCAN_UDP_PORT",port)
    #click.echo("%s %u %s %u" % (host,port,parent_host,parent_port))
    smc=synscanMotors.synscanMotors(UDP_IP,UDP_PORT)
    smc.track(azSpeed,altSpeed)

