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

``PacketAuthenticate "auth"``
=============================
Perform authentication.

Direction of Transfer
---------------------
Client to server only.

Data Members
------------
 * ``username``
    Username to authenticate for.

 * ``password``
   Password for authentication.

``PacketDeauthenticate "deauth"``
=================================
Perform user deauthenticate.

Direction of Transfer
---------------------
Bidrectional.

Data Members
------------
None.

``PacketLogin "login"``
========================
Inform the client a user has logged in.

Direction of Transfer
---------------------
Server to client only.

Data Members
------------
 * ``username``
   Username of user who has logged in.

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
