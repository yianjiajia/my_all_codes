# -*-coding:utf8-*-
from oslo_config import cfg
from keystoneclient.auth.identity import v3
from keystoneclient import session
from neutronclient.v2_0 import client as neutron_client

CONF = cfg.CONF
auth = [
    cfg.StrOpt('keystone_auth_url',
               default='http://192.168.56.56:5000/v3', help=''),
    cfg.StrOpt('username', default='admin', help=''),
    cfg.StrOpt('password', default='password', help=''),
    cfg.StrOpt('project_name', default='admin', help=''),
    cfg.StrOpt('user_domain_id', default='default', help=''),
    cfg.StrOpt('project_domain_name', default='default', help='')
]
CONF.register_opts(auth)


class OpenstackApi(object):
    def __init__(self, auth_url=CONF.keystone_auth_url, username=CONF.username,
                 password=CONF.password,
                 project_name=CONF.project_name,
                 user_domain_id=CONF.user_domain_id,
                 project_domain_name=CONF.project_domain_name):
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.project_name = project_name
        self.user_domain_id = user_domain_id
        self.project_domain_name = project_domain_name

    def auth(self):
        auth = v3.Password(auth_url=self.auth_url, username=self.username,
                           password=self.password,
                           project_name=self.project_name,
                           user_domain_id=self.user_domain_id,
                           project_domain_name=self.project_domain_name)
        return auth

    def get_sessionToken(self):
        auth = self.auth()
        token_session = session.Session(auth=auth)
        return token_session

    def get_router_bandwidth(self, router_uuid, token_session=None, region_name=None):
        router_bandwidth = None
        if not token_session:
            token_session = self.get_sessionToken()
        neutron = neutron_client.Client(session=token_session, region_name=region_name)
        router = neutron.show_router(router_uuid)
        if router.get('router'):
            router_bandwidth = router['router']['bandwidth']
        return router_bandwidth


