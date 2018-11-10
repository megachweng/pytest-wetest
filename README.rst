=============
pytest-wetest
=============

.. image:: https://img.shields.io/pypi/v/pytest-wetest.svg
    :target: https://pypi.org/project/pytest-wetest
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-wetest.svg
    :target: https://pypi.org/project/pytest-wetest
    :alt: Python versions

.. image:: https://travis-ci.org/megachweng/pytest-wetest.svg?branch=master
    :target: https://travis-ci.org/megachweng/pytest-wetest
    :alt: See Build Status on Travis CI

Welian API Automation test framework pytest plugin

----

Features
--------

* Json report
* Atomic test suit
* custom node id
* docstring based metadata

Notice
------------

breed server, the backend test visualization server of this plugin is not open source,
please consider build your own or just leave *breed_server* options empty.

Requirements
------------

* \*nix based system
* python >=3.6 python3.7 is required if you want set none-ascii **options** in **pytest.ini**
* pytest >=3.7

Installation
------------

You can install "pytest-wetest" via `pip`_ from `PyPI`_::

    $ pip install pytest-wetest


Usage
-----

For more details please check on `documentation site`_

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-wetest" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/megachweng/pytest-wetest/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
.. _`documentation site`: https://pytest-wetest.readthedocs.io/en/latest/
