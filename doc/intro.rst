Intro
=====

What is DeliveryBoy
-------------------

DeliveryBoy is a lightweight and transparent intermediary for executing a Python
callable -- a function or method -- in a new Python process such that a
developer using this intermediary does not have to care about how the object and
modules are passed.

The new Python process is started by a transport command yielding a wide range
of applications, e.g.:

- Execution as a different user via ``sudo``.
- Execution on a remote host via ``ssh``.
- Execution on a HPC cluster via ``bsub`` (in case of LSF).

The base assumptions for this implementation are:

- On the target host a compatible version of Python is installed.
- On the target host the Python environment contains the ``deliveryboy``
  package.
- The Python environment on the source and target hosts are identical (aka. same
  modules installed).
- Only the callable, module names for modules in the (virtual) environment and
  modules from outside the environment need to be transported.

.. uml:: process.puml

Acknowledgement
---------------

This project was inspired by:

- `sudo.py <https://gist.github.com/barneygale/8ff070659178135b10b5e202a1ecaa3f>`_
  by `Barney Gale <https://gist.github.com/barneygale>`_
- flowGuide2 by `Anselm Kruis <https://github.com/akruis>`_