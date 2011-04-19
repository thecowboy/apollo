#
# Copyright (C) 2011 by Tony Young
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import uuid
import logging

from tornado.options import options

from pika.adapters import TornadoConnection
from pika import PlainCredentials, ConnectionParameters, BasicProperties

from apollo.server.component import Component
from apollo.server.models.geography import Realm, Tile, Chunk

from apollo.server.protocol.packet import ORIGIN_INTER
from apollo.server.protocol.packet.meta import deserializePacket

from apollo.server.messaging import FakeSession

from apollo.server.models import meta
from apollo.server.models.auth import User

class Bus(Component):
    """
    Apollo's message bus system.
    """
    def __init__(self, core):
        super(Bus, self).__init__(core)

        self.ready = False

        self.busName = uuid.uuid4().hex

        self.parameters = ConnectionParameters(
            credentials=PlainCredentials(
                options.amqp_username,
                options.amqp_password
            ),
            host=options.amqp_host,
            port=options.amqp_port,
            virtual_host=options.amqp_vhost
        )

    def go(self):
        self.amqp = TornadoConnection(
            parameters=self.parameters,
            on_open_callback=self.on_amqp_connection_open
        )

    def on_amqp_connection_open(self, conn):
        self.amqp.channel(self.on_amqp_channel_open)

    def on_amqp_channel_open(self, channel):
        self.channel = channel

        self.declareQueue("inter", self.on_queue_declared)

    def on_queue_declared(self, something):
        self.channel.basic_consume(
            consumer_callback=self.on_inter_message,
            queue="inter",
            no_ack=False
        )

        self.channel.queue_bind(
            exchange="amq.topic",
            queue="inter",
            routing_key="inter.#"
        )
        self.ready = True
        logging.info("Message bus ready.")

    def send(self, dest, packet):
        """
        Send a packet to a specific destination.

        :Parameters:
             * ``dest``
               Destination. Prefixed with ``cross.`` for cross-server
               communication and ``user.`` for direct user messaging.

             * ``packet``
               Packet to send.
        """
        packet_dump = packet.dump()
        logging.debug("Sending to %s: %s" % (dest, packet_dump))
        self.channel.basic_publish(
            exchange="amq.topic",
            routing_key=dest,
            body=packet_dump,
            properties=BasicProperties(
                delivery_mode=2
           )
        )

    def declareQueue(self, queue, callback=None):
        self.channel.queue_declare(
            queue=queue,
            auto_delete=False,
            callback=callback
        )

    def bindQueue(self, queue, dest, callback=None):
        logging.debug("Binding %s to %s" % (queue, dest))
        self.channel.queue_bind(
            exchange="amq.topic",
            queue=queue,
            routing_key=dest,
            callback=callback
        )

    def unbindQueue(self, queue, dest, callback=None):
        logging.debug("Unbinding %s from %s" % (queue, dest))
        self.channel.queue_unbind(
            exchange="amq.topic",
            queue=queue,
            routing_key=dest,
            callback=callback
        )

    def deleteQueue(self, queue):
        logging.debug("Deleting queue %s" % queue)
        self.channel.queue_delete(queue=queue)

    def on_inter_message(self, channel, method, header, body):
        """
        Process an "inter" message.
        """
        sess = meta.Session()

        channel.basic_ack(delivery_tag=method.delivery_tag)

        prefixparts = method.routing_key.split(".")

        if prefixparts[0] != "inter":
            # this is not an inter frame
            return

        packet = deserializePacket(body)
        packet._origin = ORIGIN_INTER

        if prefixparts[1] == "user":
            user = sess.query(User).get(prefixparts[2])
            packet.dispatch(self.core, FakeSession(user.id))
        elif prefixparts[1] == "tile":
            for user in sess.query(User).filter(User.location_id == prefixparts[2]):
                packet.dispatch(self.core, FakeSession(user.id))
        elif prefixparts[1] == "group":
            for user in sess.query(User).filter(User.group_id == prefixparts[2]):
                packet.dispatch(self.core, FakeSession(user.id))
        elif prefixparts[1] == "realm":
            for user in sess.query(User).filter(User.location_id == Tile.id).filter(Tile.chunk_id == Chunk.id).filter(Chunk.realm_id == Realm.id).filter(Realm.id == prefixparts[2]):
                packet.dispatch(self.core, FakeSession(user.id))
        elif prefixparts[1] == "global":
            for user in sess.query(User):
                packet.dispatch(self.core, FakeSession(user.id))

    def broadcastEx(self, packet):
        self.send("ex.global", packet)

    def broadcastInter(self, packet):
        self.send("inter.global", packet)

    def globalBind(self, session, callback=None):
        self.bindQueue("ex-%s" % session.id, "ex.global", callback)

    def globalUnbind(self, session, callback=None):
        self.unbindQueue("ex-%s" % session.id, "ex.global", callback)
