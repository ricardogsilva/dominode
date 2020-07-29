================================
Extra DomiNode scripts and tests
================================

=======
Install
=======

These use `poetry`_, so clone this project, install poetry and then::

    cd extra/dominode-extra
    poetry install


=====
Usage
=====

This package installs the `dominode-admin` CLI tool. Use it like this::

    poetry run dominode-admin --help


+++++++++++++++++++++++++++++++++++++
Bootstrapping DomiNode infrastructure
+++++++++++++++++++++++++++++++++++++

In order to bootstrap the DomiNode infrastructure either::

    poetry run dominode-admin bootstrap


Or bootstrap each resource individually::

    poetry run dominode-admin db bootstrap
    poetry run dominode-admin minio bootstrap



=============
Running tests
=============

This package uses `pytest`_, so to run tests::

    poetry run pytest

.. _poetry: https://python-poetry.org/
.. _pytest: https://docs.pytest.org/en/latest/