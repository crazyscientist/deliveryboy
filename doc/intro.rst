Intro
=====

What is DeliveryBoy
-------------------

DeliveryBoy is a lightweight and transparent intermediary for executing a Python
callable in a new Python process such that a developer using this intermediary
does not have to care.

The new Python process is started by a transport command yield a wide range of
applications, e.g.:

- Execution as a different user by `sudo`.
- Execution on a remote host by `ssh`.
- Execution on a HPC cluster by `bsub` (in case of LSF).

The base assumption for the intermediary is that on the target host a compatible
version of Python and a similar (virtual-) environment including the
dependencies of this package are present. Everything else will get pickled and
provided in the new Python process.

Acknowledgement
---------------

This project was inspired by:

- `sudo.py <https://gist.github.com/barneygale/8ff070659178135b10b5e202a1ecaa3f>`_
  by `Barney Gale <https://gist.github.com/barneygale>`_
- flowGuide2 by `Anselm Kruis <https://github.com/akruis>`_