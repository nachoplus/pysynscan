pysynscan
=========

A pure python3 implementation of skywatcher synscan motor protocol. Tested on SkyWatcher AZ-GTI mount and open-synscan project

Instalation
-----------
From sources::

    git clone https://github.com/nachoplus/pysynscan.git
    python3 setup.py install

Use
---

Several code examples are in examples directory

Also some CLI (command lines interface) are provided:

* synscanGoto::

    Usage: synscanGoto [OPTIONS]

      Do a GOTO to a desired azimuth/altitude

    Options:
      --host TEXT       Synscan mount IP address
      --port INTEGER    Synscan mount port
      --azimuth FLOAT   Azimuth (degrees)
      --altitude FLOAT  Altitude (degrees)
      --sync BOOLEAN    Wait until finished
      --help            Show this message and exit.

* synscnaTrack::

    Usage: synscanTrack [OPTIONS]

      Move at desired speed (degrees per second)

    Options:
      --host TEXT       Synscan mount IP address
      --port INTEGER    Synscan mount port
      --azspeed FLOAT   Azimuth speed (degrees per second)
      --altspeed FLOAT  Altitude speed (degrees per second)
      --help            Show this message and exit.
