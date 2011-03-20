=================
Packets in Apollo
=================

The following packets are defined:

``PacketHeartbeat "heartbeat"``
===============================
Inform the server the client is still active.

Direction of Transfer
---------------------
Client to server.

Data Members
------------
None.

``PacketError "error"``
=======================
Inform the client an error has occured.

Direction of Transfer
---------------------
Server to client only.

Data Members
------------
 * ``msg``
   Error message.

 * ``severity``
   Severity of the error -- PacketError.WARN to emit only a console message and
   PacketError.ERROR to close the client connection.

``PacketLogin "login"``
========================
Log into the server, or inform the client a user has logged in.

Direction of Transfer
---------------------
Bidirectional.

Data Members
------------
 * ``username``
   Username of user who has logged in (empty if it is the connected client's
   packet).

 * ``pwhash``
   Password hashed with client and server nonce (client to server only).

 * ``nonce``
   Client nonce (client to server only).

``PacketLogout "logout"``
=========================
Log out of the server, or inform the client a user has logged out.

Direction of Transfer
---------------------
Bidirectional.

Data Members
------------
 * ``username``
   Username of user who has logged out (empty if it is the connected client's
   packet).

``PacketChat "chat"``
=====================
Send the client a chat message, or ask the server to relay a chat message.

Direction of Transfer
---------------------
Bidirectional.

Data Members
------------
 * ``target``
   Target of message if from client; origin of message if from server.

 * ``msg``
   Message body.

``PacketKick "kick"``
=====================
Ask the server to kick a client.

Direction of Transfer
---------------------
Client to server only.

Data Members
------------
 * ``target``
   User to kick.

 * ``msg``
   Reason for kick.

``PacketInfo "info"``
=====================
Request information about the current tile from the server, or send the client
information about the current tile.

Direction of Transfer
---------------------
Bidirectional.

Data Members
------------
 * ``location``
   Location of the tile (x, y and realm).

 * ``tileinfo``
   Information about the tile.

 * ``things``
   Things present at the tile.

 * ``extents``
   Realm extents.

``PacketUser "user"``
=====================
Request basic information about either an arbitrary user from the server or the
current user, or send the client user information.

Direction of Transfer
---------------------
Bidirectional.

Data Members
------------
 * ``target``
   User to request information about. Empty if requesting information about
   current user.

 * ``name``
   User's name. In most cases will be the same value as ``target``.

 * ``level``
   Level of the user.

 * ``hp``
   User's HP, in { current, max }.

 * ``ap``
   User's AP, in { current, max }.

 * ``xp``
   User's XP, in { current, max }.
