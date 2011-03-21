============
Introduction
============

Apollo is an isometric HTML5 multiplayer game engine implemented with Python_ on
the server side using Tornado_, ZeroMQ_ and MongoDB_, and on the client side
with the excellent Dojo_ framework.

Server
======

Asynchronous
------------
The Apollo server is, for the most part, asynchronous, thanks to the Tornado_
web server. Operations that may block the server are performed in other
processes, such as chunk rendering.

Chunking
--------
Apollo renders tiles in chunks of 64 (stride of 8x8) for the client to render.

(Eventual) Scalability
----------------------
Apollo is (mostly) designed to be scalable. It uses ZeroMQ_ for passing data
around channels and cross-server communication. While, currently, Apollo does
not completely assure seamless scalability, this is one of our key concerns.

Client
======

Largely Compatible
------------------
The client utilizes the Dojo_ framework for a lot of abstraction, which has been
tried and tested on a multitude of modern browsers.

No Flash, No Java
-----------------
The Apollo client does not need anything more than a modern browser to run.

.. _Python: http://www.python.org
.. _Tornado: http://www.tornadoweb.org
.. _ZeroMQ: http://www.zeromq.org
.. _MongoDB: http://www.mongodb.org
.. _Dojo: http://www.dojotoolkit.org
