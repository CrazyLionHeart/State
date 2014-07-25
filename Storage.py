#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from State.config import config

    from pymongo.mongo_replica_set_client import MongoReplicaSetClient
    from pymongo.errors import AutoReconnect, ConnectionFailure
    from pymongo.read_preferences import ReadPreference
    from pymongo import ASCENDING, DESCENDING
    from bson.json_util import dumps
    import json
    import logging
    import time

except ImportError as e:
    raise e


class Storage(object):

    def __init__(self, collection):
        self.mongodb = config['mongodb']
        self.host = ",".join(self.mongodb['host'])
        self.replicaSet = self.mongodb['replicaSet']
        self.writeConcern = self.mongodb['writeConcern']
        self.journal = self.mongodb['journal']
        self.readPreference = ReadPreference.SECONDARY_PREFERRED
        self.collection = collection

        logging.debug(self.collection)

    def list(self, filters=None, limit=None, sort=None, skip=None,
             returns=None):

        try:
            client = MongoReplicaSetClient(self.host,
                                           replicaSet=self.replicaSet,
                                           use_greenlets=True,
                                           w=self.writeConcern,
                                           j=self.journal,
                                           read_preference=self.readPreference,
                                           slave_okay=True,
                                           connectTimeoutMS=200)
        except ConnectionFailure as e:
                logging.exception("Connection falure error reached: %r" % e)
                raise Exception(e)

        db = client[self.mongodb['database']]
        db.read_preference = self.readPreference
        collection = db[self.collection]

        kwargs = dict()

        if limit:
            kwargs['limit'] = limit

        if skip:
            kwargs['skip'] = skip

        if returns:
            kwargs['fields'] = returns

        for i in xrange(self.mongodb["max_autoreconnect"]):
            try:
                logging.debug("""Trying to send data.
                              Alive hosts: %r""" % client)

                if filters:
                    results = collection.find(filters, **kwargs)
                else:
                    results = collection.find(**kwargs)

                if sort:
                    if sort['direction'] == 'asc':
                        results = results.sort(sort['key'], ASCENDING)
                    else:
                        results = results.sort(sort['key'], DESCENDING)

                return json.loads(dumps(results))

            except AutoReconnect:
                time.sleep(pow(2, i))
                logging.debug("""Autoreconnect error reached.
                          Trying to resend data by timeout.
                          Previous alive hosts: %r""" % client)

        client.close()
        logging.exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")
        raise Exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")

    def count(self):

        try:
            client = MongoReplicaSetClient(self.host,
                                           replicaSet=self.replicaSet,
                                           use_greenlets=True,
                                           w=self.writeConcern,
                                           j=self.journal,
                                           read_preference=self.readPreference,
                                           slave_okay=True,
                                           connectTimeoutMS=200)
        except ConnectionFailure as e:
                logging.exception("Connection falure error reached: %r" % e)
                raise Exception(e)

        db = client[self.mongodb['database']]
        db.read_preference = self.readPreference
        collection = db[self.collection]

        for i in xrange(self.mongodb["max_autoreconnect"]):
            try:
                logging.debug("""Trying to send data.
                              Alive hosts: %r""" % client)

                return collection.find().count()
            except AutoReconnect:
                time.sleep(pow(2, i))
                logging.debug("""Autoreconnect error reached.
                          Trying to resend data by timeout.
                          Previous alive hosts: %r""" % client)

        client.close()
        logging.exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")
        raise Exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")

    def modify(self, doc_pin, state):

        try:
            client = MongoReplicaSetClient(self.host,
                                           replicaSet=self.replicaSet,
                                           use_greenlets=True,
                                           w=self.writeConcern,
                                           j=self.journal,
                                           read_preference=self.readPreference,
                                           slave_okay=True,
                                           connectTimeoutMS=200)
        except ConnectionFailure as e:
                logging.exception("Connection falure error reached: %r" % e)
                raise Exception(e)

        db = client[self.mongodb['database']]
        db.read_preference = self.readPreference
        collection = db[self.collection]

        for i in xrange(self.mongodb["max_autoreconnect"]):
            try:
                logging.debug("""Trying to send data.
                              Alive hosts: %r""" % client)

                query = {'doc_pin': doc_pin}
                data = {'doc_pin': doc_pin, 'state': state}

                results = collection.update(query, data, upsert=True)
                return json.loads(dumps(results))

            except AutoReconnect:
                time.sleep(pow(2, i))
                logging.debug("""Autoreconnect error reached.
                          Trying to resend data by timeout.
                          Previous alive hosts: %r""" % client)

        client.close()
        logging.exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")
        raise Exception("""Error: Failed operation!
                      Is anybody from mongo servers alive?""")
