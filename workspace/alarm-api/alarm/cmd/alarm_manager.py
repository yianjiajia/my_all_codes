# -*- coding:utf-8 -*-
"""Starter script for alarm OS API."""

import sys
from oslo_config import cfg
from oslo_log import log as logging
from alarm import config
from alarm import service
from alarm import utils

CONF = cfg.CONF
workers = [
    cfg.IntOpt('workers',
               default=1,
               help=''),
]
CONF.register_opts(workers)


def main():
    config.parse_args(sys.argv)
    logging.setup(CONF, "alarm")
    utils.monkey_patch()
    server = service.WSGIService('alarm_api', use_ssl=False)
    service.serve(server, workers=CONF.workers)
    service.wait()


if __name__ == "__main__":
    main()

