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
