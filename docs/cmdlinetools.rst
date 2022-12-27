By defaults connection parameters are::

    SYNSCAN_UDP_IP=192.168.4.1
    SYNSCAN_UDP_PORT=11880
    SYNSCAN_LOGGING_LEVEL=INFO

This values can be changed via enviroment vars::

    export SYNSCAN_UDP_IP=192.168.5.1
    export SYNSCAN_UDP_PORT=11880
    export SYNSCAN_LOGGING_LEVEL=WARNING

Also every CLI command has --host and --port parameters. Enviromental vars take precedence.

.. click:: synscan.scripts.cli:goto
   :prog: synscanGoto
   :nested: full

.. click:: synscan.scripts.cli:track
   :prog: synscanTrack
   :nested: full

.. click:: synscan.scripts.cli:stop
   :prog: synscanStop
   :nested: full

.. click:: synscan.scripts.cli:watch
   :prog: synscanWatch
   :nested: full

.. click:: synscan.scripts.cli:synchronize
   :prog: synscanSync
   :nested: full

.. click:: synscan.scripts.cli:switch
   :prog: synscanSwitch
   :nested: full
