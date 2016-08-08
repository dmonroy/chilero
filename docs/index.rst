.. Chilero documentation master file, created by
   sphinx-quickstart on Thu Jun 23 21:57:13 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Chilero!
===================

Chilero is a minimalistic HTTP framework, a thin layer on top of the aiohttp_
framework. Based on asyncio_, chilero works with single-threaded concurrent
code using coroutines.

Simplicity is core principle of chilero (and must be for the eternity), just
take a look at the following sample and judge by yourself:


.. code-block:: python

   from chilero import web


   class Hello(web.View):

       def get(self):
           return web.Response('Hello World!')


   routes = [
       ['/', Hello]
   ]

   web.run(web.Application, routes)


Beyond the constraints given by asyncio and aiohttp, chilero is not imposing
the usage of any additional package nor platform, you should be free to
integrate with any third party library for asyncio_.


Contents:
---------

.. toctree::
   :maxdepth: 2

   api.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _aiohttp: http://aiohttp.readthedocs.io/
.. _asyncio: http://asyncio.org/
