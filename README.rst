pysynscan
=========

A pure python3 implementation of skywatcher synscan motor protocol. Tested on SkyWatcher AZ-GTI mount and open-synscan project (https://github.com/vsirvent/Open-Synscan)

SkyWatcher made some of their code public in (https://github.com/skywatcher-pacific/skywatcher_open) even a  C# !WinForm python interpreter application exist. See (https://code.google.com/archive/p/skywatcher/wikis/Programmable.wiki) but, been a special interpreter, python integration is limited. This project try to fill this gap.
 

Installation
------------
From sources::

    git clone https://github.com/nachoplus/pysynscan.git
    python3 setup.py install

From pip::

    pip install synscan

Use
---
Code sample::

    import synscan
    '''Goto example'''
    smc=synscan.motors()
    #Syncronize mount actual position to (0,0)
    smc.set_pos(0,0)
    #Move forward and wait to finish
    smc.goto(30,30,syncronous=True)
    #Return to original position and exit without wait
    smc.goto(0,0,syncronous=False)


More code examples are in examples directory.

Several CLI (command lines interface) are provided::

    synscanGoto 32 10
    synscanTrack 0 1
    synscanStop
    synscanWatch
    synscanSync 10 12
    synscanSwitch 1

Documentation
-------------

See the full documentation [https://nachoplus.github.io/pysynscan]



