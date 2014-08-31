#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from State.config import config
    from State.Storage import Storage

    import json
    import logging

    from stompest.sync import Stomp
    from stompest.config import StompConfig
    from stompest.protocol import StompSpec

    from raven import Client

except ImportError as e:
    raise e

activemq = config['activemq']
default_uri = '''failover:(tcp://%(host)s:%(port)d,tcp://%(host)s:%(port)d)?randomize=%(randomize)s,startupMaxReconnectAttempts=%(startupMaxReconnectAttempts)d,initialReconnectDelay=%(initialReconnectDelay)d,maxReconnectDelay=%(maxReconnectDelay)d,maxReconnectAttempts=%(maxReconnectAttempts)d''' % activemq[
    'stomp']

queue = "/topic/%s" % config['queue']['BotNet']

logger = logging.getLogger(__name__)

dsn = 'http://%(public)s:%(private)s@%(host)s' % config['Raven']
client = Client(dsn)


class Consumer(object):

    def __init__(self, config=None):
        if config is None:
            config = StompConfig(default_uri)
        else:
            config = StompConfig(config)
        self.config = config

    def run(self):
        client = Stomp(self.config)
        client.connect()
        headers = {
            # client-individual mode is necessary for concurrent processing
            # (requires ActiveMQ >= 5.2)
            StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL,
            # the maximal number of messages the broker will let you work on at
            # the same time
            'activemq.prefetchSize': '100',
        }
        client.subscribe(queue, headers)

        while True:
            frame = client.receiveFrame()
            data = json.loads(frame.body)
            body = data.get('body')
            if body and body.get('func_name') == 'updater.receive':
                args = json.loads(body.get('func_args'))
                if args.get('data'):
                    doc_pin = args['data']['objects'][0]['id']
                    Storage().remove(doc_pin)
            client.ack(frame)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Consumer().run()
