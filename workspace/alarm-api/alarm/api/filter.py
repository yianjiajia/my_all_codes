# -*- coding:utf-8 -*-
"""
Common Auth Middleware.

"""




from oslo_config import cfg
from oslo_log import log as logging
from oslo_middleware import request_id
from oslo_serialization import jsonutils
import webob.dec
import webob.exc


filter_opts = [
    cfg.StrOpt('filter_strategy',
               default='noauth',
               help='''
The strategy to use for auth: keystone, noauth (deprecated), or
noauth2. Both noauth and noauth2 are designed for testing only, as
they do no actual credential checking. noauth provides administrative
credentials regardless of the passed in user, noauth2 only does if
'admin' is specified as the username.
'''),
]

CONF = cfg.CONF
CONF.register_opts(filter_opts)

LOG = logging.getLogger(__name__)


def _load_pipeline(loader, pipeline):
    filters = [loader.get_filter(n) for n in pipeline[:-1]]
    app = loader.get_app(pipeline[-1])
    filters.reverse()
    for filter in filters:
        app = filter(app)
    return app


def pipeline_factory(loader, global_conf, **local_conf):
    pipeline = local_conf[CONF.filter_strategy]
    pipeline = pipeline.split()
    return _load_pipeline(loader, pipeline)
