Geography
=========

Apollo's internal representation of geography is split into several layers,
which are as follows:

Base
----
The base layer contains terrain data. It is delivered to the client as a series
of chunks, rather than individually tile-by-tile. The base layer is assumed to
be relatively immutable.

This layer contains basic terrain data, such as grass, sea, beaches and so
forth.

Entity
------
The entity layer contains all the entities on the map. This layer is delivered
to the client as positional data with sprites, rather than chunks. The entity
layer is assumed to be ephemeral.

This layer contains objects such as houses, farms, etc.
