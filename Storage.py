#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from State.config import config

    from pymongo.mongo_replica_set_client import MongoReplicaSetClient
    from pymongo.errors import ConnectionFailure, OperationFailure
    from pymongo.errors import InvalidDocument
    from pymongo import ASCENDING, DESCENDING
    from bson.json_util import dumps
    import json
    import logging

except ImportError as e:
    raise e

logger = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, collection=None, *args, **kwargs):
        try:
            mongodb = config['mongodb']
            host = ",".join(mongodb['host'])
            replicaSet = mongodb['replicaSet']
            writeConcern = mongodb['writeConcern']
            journal = mongodb['journal']

            client = MongoReplicaSetClient(host,
                                           replicaSet=replicaSet,
                                           use_greenlets=True,
                                           w=writeConcern,
                                           j=journal,
                                           slave_okay=True,
                                           connectTimeoutMS=200)

            self.db = client[mongodb['database']]

            if collection:
                self.setCollection(collection)

        except ConnectionFailure as e:
            raise Exception("Connection falure error reached: %r" % e)

    def getCollections(self):
        return self.db.collection_names(include_system_collections=False)

    def setCollection(self, collection):
        if collection:
            self.collection = self.db[collection]
        else:
            raise Exception("Collection name not defined")

    def list(self, filters=None, limit=None, sort=None, skip=None,
             returns=None):

        kwargs = dict()

        if limit:
            kwargs['limit'] = limit

        if skip:
            kwargs['skip'] = skip

        if returns:
            kwargs['fields'] = returns

        if not filters:
            filters = {}

        results = self.collection.find(filters, **kwargs)

        logger.debug("Result: %s" % results)

        if sort:
            if sort['direction'] == 'asc':
                key = ASCENDING
            else:
                key = DESCENDING
            return json.loads(dumps(results.sort(sort['key'], key)))
        else:
            return json.loads(dumps(results))

    def count(self):

        try:
            result = self.db.command('collstats', self.collection)
            return result['count']
        except (OperationFailure, InvalidDocument):
            return 0

    def insert(self, doc_pin):

        results = self.collection.insert({'doc_pin': doc_pin})

        return json.loads(dumps(results))

    def remove(self, doc_pin):
        results = []
        for element in self.getCollections():
            self.setCollection(element)
            results.append(self.collection.remove({'doc_pin': doc_pin},))

        return json.loads(dumps(results))
