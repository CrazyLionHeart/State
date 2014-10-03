#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from raven.contrib.flask import Sentry
    from raven.middleware import Sentry as SentryMiddleware

    from flask import jsonify, url_for, request

    from State.JsonApp import make_json_app, crossdomain
    from State.Storage import Storage
    from State.config import config

    import math
    import json
    import re

except ImportError as e:
    raise e

dsn = "http://%s:%s@%s" % (config['Raven']['public'],
                           config['Raven']['private'],
                           config['Raven']['host'])

app = make_json_app(__name__)
app.config['SENTRY_DSN'] = dsn
sentry = Sentry(dsn=dsn, logging=True)
sentry.init_app(app)
app.wsgi = SentryMiddleware(app.wsgi_app, sentry.client)


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
            try:
                links.append(
                    dict(methods=methods, url=urllib.unquote(url),
                         docstring=docstring))
            except:
                links.append(
                    dict(methods=methods, url=urllib.unquote(url),
                         docstring=docstring))

    return jsonify(results=links)


@app.route('/list/<user_login>', methods=['GET', 'POST'])
@crossdomain(origin='*')
def list(user_login):
    u'''Возвращает список прочитанных пользователем документов'''

    if request.method == 'GET':
        app.logger.debug("GET arguments: %s" % request.args)

        page = int(request.args.get('page', 1))
        rows = int(request.args.get('rows', 1000))
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

    if request.method == 'POST':

        app.logger.debug(" POST arguments: %s" % request.form)

        page = int(request.form.get('page', 1))
        rows = int(request.form.get('rows', 1000))
        sidx = request.form.get("sidx")
        sord = request.form.get("sord")
        _search = request.form.get("_search")
        searchField = request.form.get("searchField")
        searchString = request.form.get("searchString")
        searchOper = request.form.get("searchOper")
        other_search = request.form.get("other_search")
        full_props = request.form.get("full_props")
        gridFilters = request.form.get("filters")
        filtersMain = request.form.get("filtersMain")
        showcols = request.form.get("showcols")
        totalrows = int(request.form.get("totalrows", 1000))

    if not gridFilters:
        gridFilters = {"groupOp": "AND", "rules": []}
    else:
        gridFilters = json.loads(gridFilters)
        app.logger.debug("Input gridFilters %s" % gridFilters)

    if not filtersMain:
        filtersMain = {"groupOp": "AND", "rules": []}
    else:
        filtersMain = json.loads(filtersMain)
        app.logger.debug("Input filtersMain %s" % filtersMain)

    if showcols:
        showcols = showcols.split(',')
        showcols = [elem for elem in showcols if elem.upper() != elem]

    filters = {}
    sort = None

    if _search:
        for rule in filtersMain['rules']:

            if not filters.get(rule['field']):
                filters[rule['field']] = []

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
                filters[rule['field']].append(
                    {'$text': {'$search': rule['data']}})
            elif rule['op'] == 'nc':
                    filters[rule['field']] = {
                        '$not': re.compile("%s" % rule['data'])}
            elif rule['op'] == 'bn':
                filters[rule['field']] = {
                    '$not': re.compile("^%s" % rule['data'])}
            elif rule['op'] == 'en':
                filters[rule['field']] = {
                    '$not': re.compile("%s$" % rule['data'])}
            elif rule['op'] == "in":
                filters[rule['field']] = {'$in': rule['data']}
            elif rule['op'] == "nin":
                filters[rule['field']] = {'$nin': rule['data']}

        if gridFilters.get('rules'):
            for rule in gridFilters['rules']:

                if not filters.get(rule['field']):
                    filters[rule['field']] = []

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
                    filters[rule['field']] = {
                        '$not': re.compile("%s" % rule['data'])}
                elif rule['op'] == 'bn':
                    filters[rule['field']] = {
                        '$not': re.compile("^%s" % rule['data'])}
                elif rule['op'] == 'en':
                    filters[rule['field']] = {
                        '$not': re.compile("%s$" % rule['data'])}
                elif rule['op'] == "in":
                    filters[rule['field']] = {'$in': rule['data']}
                elif rule['op'] == "nin":
                    filters[rule['field']] = {'$nin': rule['data']}
    else:
        filters = None

    app.logger.debug("Filters: %s" % filters)

    if sidx:
        if sord:
            sort = dict(key=sidx, direction=sord)

    skip = int((page - 1) * rows)

    all_data = Storage(user_login).list(filters, rows, sort, skip, showcols)
    count_data = len(all_data)

    total = int(math.ceil(count_data / float(rows)))

    return jsonify(dict(total=total, page=page, rows=all_data,
                        records=count_data))


@app.route('/mark/<doc_pin>/<user_login>', methods=['POST'])
@crossdomain(origin='*')
def mark(doc_pin, user_login):
    u'''Помечает документа прочитанным пользователем'''
    results = Storage(user_login).insert(doc_pin)
    return jsonify(results=results)


@app.route('/mark/<doc_pin>', methods=['CLEAR'])
@crossdomain(origin='*')
def clear(doc_pin):
    u'''Очищает пометку прочитанности для всех пользователей'''
    results = Storage().remove(doc_pin)
    return jsonify(results=results)
