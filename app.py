#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from gevent import monkey
    monkey.patch_all()

    from raven.contrib.flask import Sentry

    from flask import jsonify, request, url_for

    from State.JsonApp import make_json_app, crossdomain
    from State.config import config

    from base64 import b64decode

    import re

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

url = 'http://%s/ajax/submitajax.php' % config["obs"]
user = 'system'
password = 'system_1234'

auth = requests.auth.HTTPBasicAuth(user, password)


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


@app.route('/list/<doc_type>/</user_login>')
@crossdomain(origin='*')
def list(doc_type, user_login):
    return jsonify(results=doc_type)


@app.route('/mark/<doc_pin>/<user_login>', methods=['POST'])
@crossdomain(origin='*')
def mark(doc_pin, user_login):
    return jsonify(results=doc_pin)
