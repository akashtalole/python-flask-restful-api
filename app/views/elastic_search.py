from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

from config import Config


def _normalize_hosts(hosts):
    """The Elasticsearch client requires a scheme, older configs only contain `host:port`"""
    if isinstance(hosts, str):
        hosts = [hosts]
    return [host if '://' in host else 'http://' + host for host in hosts]


class FlaskElasticsearch:
    """
    Minimal Flask extension that lazily creates an Elasticsearch client from the
    app config and proxies attribute access to it.
    """

    def __init__(self, app=None, **kwargs):
        self._options = kwargs
        self._client = None
        self._hosts = None
        self._http_auth = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app, **kwargs):
        app.config.setdefault('ELASTICSEARCH_HOST', 'localhost:9200')
        app.config.setdefault('ELASTICSEARCH_HTTP_AUTH', None)
        self._options.update(kwargs)
        self._hosts = _normalize_hosts(app.config['ELASTICSEARCH_HOST'])
        self._http_auth = app.config['ELASTICSEARCH_HTTP_AUTH']
        self._client = None

    @property
    def elasticsearch(self):
        if self._client is None and self._hosts is not None:
            options = dict(self._options)
            if self._http_auth:
                options['basic_auth'] = self._http_auth
            self._client = Elasticsearch(hosts=self._hosts, **options)
        return self._client

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)
        client = self.elasticsearch
        if client is None:
            raise RuntimeError('Elasticsearch client is not initialised')
        return getattr(client, item)


client = FlaskElasticsearch()


def connect_from_config():
    """Create connection for `elasticsearch_dsl`"""
    hosts = _normalize_hosts(Config.ELASTICSEARCH_HOST)
    es_store = Elasticsearch(hosts)
    connections.create_connection(hosts=hosts)

    return es_store
