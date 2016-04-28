# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Nova base exception handling.

Includes decorator for re-raising Nova-type exceptions.

SHOULD include dedicated exception logging.

"""
import sys
from oslo_config import cfg
from oslo_log import log as logging
import six
from alarm.i18n import _, _LE


LOG = logging.getLogger(__name__)

exc_log_opts = [
    cfg.BoolOpt('fatal_exception_format_errors',
                default=False,
                help='Make exception message format errors fatal'),
]

CONF = cfg.CONF
CONF.register_opts(exc_log_opts)


class AlarmException(Exception):
    """Base Naas Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.

    """
    msg_fmt = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs

            except Exception:
                exc_info = sys.exc_info()
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception(_LE('Exception in string format operation'))
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))  # noqa

                if CONF.fatal_exception_format_errors:
                    six.reraise(*exc_info)
                else:
                    # at least get the core message out if something happened
                    message = self.msg_fmt

        super(AlarmException, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full NovaException message, (see __init__)
        return self.args[0]


class Invalid(AlarmException):
    msg_fmt = _("Unacceptable parameters.")
    code = 400


class InvalidInput(Invalid):
    msg_fmt = _("Invalid input received: %(reason)s")


class InvalidAPIVersionString(Invalid):
    msg_fmt = _("API Version String %(version)s is of invalid format. Must "
                "be of format MajorNum.MinorNum.")


class PasteAppNotFound(AlarmException):
    msg_fmt = _("Could not load paste app '%(name)s' from %(path)s")


class ConfigNotFound(AlarmException):
    msg_fmt = _("Could not find config at %(path)s")


class InvalidContentType(Invalid):
    msg_fmt = _("Invalid content type %(content_type)s.")


class VersionNotFoundForAPIMethod(Invalid):
    msg_fmt = _("API version %(version)s is not supported on this method.")


class MalformedRequestBody(AlarmException):
    msg_fmt = _("Malformed message body: %(reason)s")


class InvalidGlobalAPIVersion(Invalid):
    msg_fmt = _("Version %(req_ver)s is not supported by the API. Minimum "
                "is %(min_ver)s and maximum is %(max_ver)s.")


