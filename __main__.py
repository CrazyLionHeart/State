#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from gevent import monkey
    monkey.patch_all()

    import sys
    import os

    path = os.path.dirname(sys.modules[__name__].__file__)
    path = os.path.join(path, '..')
    sys.path.insert(0, path)

    from State.app import app
    import logging

except ImportError, e:
    raise e

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
