.. pysynscan documentation master file, created by
   sphinx-quickstart on Sun Aug  2 19:33:47 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pysynscan's documentation!
=====================================

.. include:: ../README.rst

Examples
========
.. automodule:: examples.goto
   :members:
   :inherited-members:


Command line utilities
======================
.. click:: synscan.scripts.cli:goto
   :prog: synscanGoto
   :nested: full

.. click:: synscan.scripts.cli:track
   :prog: synscanTrack
   :nested: full

.. click:: synscan.scripts.cli:stop
   :prog: synscanStop
   :nested: full

.. click:: synscan.scripts.cli:show
   :prog: synscanShow
   :nested: full

.. click:: synscan.scripts.cli:syncronize
   :prog: synscanSync
   :nested: full

API Reference
=============
.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
