#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from gevent import monkey
    monkey.patch_all()

    from raven.contrib.flask import Sentry

    from flask import jsonify, url_for, request

    from State.JsonApp import make_json_app, crossdomain
    from State.Storage import Storage
    from State.config import config

    import math
    import json
    import logging

except ImportError, e:
    raise e

dsn = "http://%s:%s@%s" % (config['Raven']['public'],
                           config['Raven']['private'],
                           config['Raven']['host'])

app = make_json_app(__name__)

app.config['SENTRY_DSN'] = dsn
app.debug = True
sentry = Sentry(app)


def search(id, messages, key):
    return [element for element in messages if element[key] == id]


@app.route('/')
@crossdomain(origin='*')
def example():
    """Помощь по API"""

    import urllib
    links = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            methods = ','.join(rule.methods)

            url = url_for(rule.endpoint, **options)
            docstring = app.view_functions[rule.endpoint].__doc__
            links.append(
                dict(methods=methods, url=urllib.unquote(url),
                     docstring=docstring))

    return jsonify(results=links)


@app.route('/list/<doc_type>')
@crossdomain(origin='*')
def list(doc_type):
    logging.debug("arguments: %s" % request.args)

    page = int(request.args.get('page', 1))
    rows = int(request.args.get('rows', 30))
    sidx = request.args.get("sidx")
    sord = request.args.get("sord")
    _search = request.args.get("_search")
    searchField = request.args.get("searchField")
    searchString = request.args.get("searchString")
    searchOper = request.args.get("searchOper")
    other_search = request.args.get("other_search")
    full_props = request.args.get("full_props")
    gridFilters = request.args.get("filters")
    filtersMain = request.args.get("filtersMain")
    showcols = request.args.get("showcols")
    totalrows = int(request.args.get("totalrows", 1000))

    if not gridFilters:
        gridFilters = {"groupOp": "AND", "rules": []}
    else:
        gridFilters = json.loads(gridFilters)

    if not filtersMain:
        filtersMain = {"groupOp": "AND", "rules": []}
    else:
        filtersMain = json.loads(filtersMain)

    showcols = showcols.split(',')

    showcols = [elem for elem in showcols if elem.upper() != elem]

    filters = {}
    sort = None

    if _search:
        for rule in filtersMain['rules']:

            if not filters.get(rule['field']):
                filters[rule['field']] = list()

            if rule['op'] == "bw":
                filters[rule['field']].append({'$regex': '^%s' % rule['data']})
            elif rule['op'] == "ew":
                filters[rule['field']].append({'$regex': '%s^' % rule['data']})
            elif rule['op'] == "eq":
                filters[rule['field']].append(rule['data'])
            elif rule['op'] == "ne":
                filters[rule['field']].append({'$ne': rule['data']})
            elif rule['op'] == "lt":
                filters[rule['field']].append({'$lt': rule['data']})
            elif rule['op'] == "le":
                filters[rule['field']].append({'$lte': rule['data']})
            elif rule['op'] == "gt":
                filters[rule['field']].append({'$gt': rule['data']})
            elif rule['op'] == "ge":
                filters[rule['field']].append({'gte': rule['data']})
            elif rule['op'] == "cn":
                filters[rule['field']].append({'$text': {'$search': rule['data']}})

        if gridFilters.get('rules'):
            for rule in gridFilters['rules']:

                if rule['op'] == "bw":
                    filters[rule['field']] = re.compile("^%s" % rule['data'])
                elif rule['op'] == "ew":
                    filters[rule['field']] = re.compile("%s$" % rule['data'])
                elif rule['op'] == "eq":
                    filters[rule['field']] = rule['data']
                elif rule['op'] == "ne":
                    filters[rule['field']] = {'$ne': rule['data']}
                elif rule['op'] == "lt":
                    filters[rule['field']] = {'$lt': rule['data']}
                elif rule['op'] == "le":
                    filters[rule['field']] = {'$lte': rule['data']}
                elif rule['op'] == "gt":
                    filters[rule['field']] = {'$gt': rule['data']}
                elif rule['op'] == "ge":
                    filters[rule['field']] = {'gte': rule['data']}
                elif rule['op'] == "cn":
                    filters[rule['field']] = re.compile("%s" % rule['data'])
                elif rule['op'] == 'nc':
                    filters[rule['field']] = {'$not': re.compile("%s" % rule['data'])}
                elif rule['op'] == 'bn':
                    filters[rule['field']] = {'$not': re.compile("^%s" % rule['data'])}
                elif rule['op'] == 'en':
                    filters[rule['field']] = {'$not': re.compile("%s$" % rule['data'])}
    else:
        filters = None

    logging.debug("Filters: %s" % filters)

    if sidx:
        if sord:
            sort = dict(key=sidx, direction=sord)

    skip = int((page - 1) * rows)

    all_data = Storage(doc_type).list(filters, rows, sort, skip, showcols)
    count_data = Storage(doc_type).count()

    total = int(math.ceil(count_data / float(rows)))

    return jsonify(dict(total=total, page=page, rows=all_data,
                        records=count_data))


@app.route('/mark/<doc_type>/<doc_pin>/<user_login>', methods=['POST'])
@crossdomain(origin='*')
def mark(doc_type, doc_pin, user_login):
    results = Storage(doc_type).set(doc_pin, user_login)
    return jsonify(results=results)


@app.route('/clear/<doc_type>/<doc_pin>/<user_login>', methods=['CLEAR'])
@crossdomain(origin='*')
def clear(doc_type, doc_pin, user_login):
    results = Storage(doc_type).clear(doc_pin, user_login)
    return jsonify(results=results)