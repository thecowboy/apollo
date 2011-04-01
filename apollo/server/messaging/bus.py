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
from functools import wraps

import uuid
import logging

from tornado.options import options

from pika.adapters import TornadoConnection
from pika import PlainCredentials, ConnectionParameters, BasicProperties

from pymongo.objectid import ObjectId

from apollo.server.component import Component

from apollo.server.protocol.packet import ORIGIN_INTER
from apollo.server.protocol.packet.meta import deserializePacket

from apollo.server.models import meta
from apollo.server.models.auth import Session, User

class Bus(Component):
    """
    Apollo's message bus system.
    """
    def __init__(self, core):
        super(Bus, self).__init__(core)

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

        self.amqp = TornadoConnection(
            parameters=self.parameters,
            on_open_callback=self.on_amqp_connection_open
        )

    def on_amqp_connection_open(self, conn):
        self.amqp.channel(self.on_amqp_channel_open)

    def on_amqp_channel_open(self, channel):
        self.channel = channel

        self.channel.exchange_declare(
            exchange="apollo",
            type="topic",
            durable=True,
            auto_delete=False,
            callback=self.on_amqp_exchange_declared
        )

    def on_amqp_exchange_declared(self, method):
        self.subscribe("inter.#", "inter", self.on_inter_message)
        logging.info("Message bus ready.")

    def on_queue_declared(self, dest, queue, callback):
        self.channel.queue_bind(
            exchange="apollo",
            queue=queue,
            routing_key=dest,
            callback=lambda *args: self.on_subscribe(queue, callback)
        )

    def handler_wrapper(self, state, fn):
        @wraps(fn)
        def _wrapper(channel, method, header, body):
            channel.basic_ack(delivery_tag=method.delivery_tag)
            fn(state["ctag"], method, header, body)
        return _wrapper

    def on_subscribe(self, queue, callback):
        state = {}
        state["ctag"] = self.channel.basic_consume(
            consumer_callback=self.handler_wrapper(state, callback),
            queue=queue,
            no_ack=False
        )

    def subscribe(self, dest, queue, callback):
        queue_name = "%s-%s" % (self.busName, queue)

        logging.info("Bound queue %s for %s" % (queue_name, dest))

        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            exclusive=False,
            auto_delete=True,
            callback=lambda *args: self.on_queue_declared(dest, "%s-%s" % (self.busName, queue), callback)
        )

    def unsubscribe(self, dest, queue):
        self.channel.queue_unbind(
            exchange="apollo",
            queue=queue,
            routing_key=dest
        )

    def unconsume(self, consumerTag):
        self.channel.basic_cancel(consumer_tag=consumerTag)

    def broadcast(self, dest, packet):
        """
        Broadcast a packet to a specific destination.

        :Parameters:
             * ``dest``
               Destination. Prefixed with ``cross.`` for cross-server
               communication and ``user.`` for direct user messaging.

             * ``packet``
               Packet to broadcast.
        """
        logging.debug("Sending to %s: %s" % (dest, packet.dump()))
        self.channel.basic_publish(
            exchange="apollo",
            routing_key=dest,
            body=packet.dump(),
            properties=BasicProperties(
                delivery_mode=2
           )
        )

    def on_inter_message(self, ctag, method, header, body):
        """
        Process an "inter" message.
        """
        prefixparts = method.routing_key.split(".")

        if prefixparts[0] != "inter":
            # this is not an inter frame
            return

        packet = deserializePacket(body)
        packet._origin = ORIGIN_INTER

        if prefixparts[1] == "user":
            for session in meta.session.find(Session, { "user_id" : ObjectId(prefixparts[2]) }):
                packet.dispatch(self.core, session)
        elif prefixparts[1] == "loc":
            for user in meta.session.find(User, { "location_id" : ObjectId(prefixparts[2]) }):
                for session in meta.session.find(Session, { "user_id" : user._id }):
                    packet.dispatch(self.core, session)
