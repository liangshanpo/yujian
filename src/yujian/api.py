import inspect

from loguru import logger

from yujian.http import Http


'''
list exchanges, queues, bindings, vhosts, users, permissions, connections and channels
show overview information
declare and delete exchanges, queues, bindings, vhosts, users and permissions
publish and get messages
close connections and purge queues
import and export configuration
'''

config = {
    'overview': {
        'uri': '/api/overview',
        'method': 'get',
        'option': {
            'columns': [
                'rabbitmq_version',
                'cluster_name',
                'queue_totals.messages',
                'object_totals.queues',
            ]
        },
    },
    'whoami': {'uri': '/api/whoami', 'method': 'get'},
    ## getable
    'get_exchange': {
        'uri': '/api/exchanges/{vhost}/{name}',
        'method': 'get',
        'mandatory': ['name'],
        'option': {'columns': ['name', 'type']},
    },
    'get_queue': {
        'uri': '/api/queues/{vhost}/{name}',
        'method': 'get',
        'mandatory': ['name'],
        'option': {'columns': ['name', 'messages']},
    },
    'get_binding': {
        'uri': '/api/bindings/{vhost}/e/{source}/{destination_char}/{destination}/{properties_key}',
        'method': 'get',
        'mandatory': ['source', 'destination_type', 'destination'],
        'option': {
            'properties_key': '~',
            'columns': ['source', 'destination', 'routing_key'],
        },
    },
    'get_vhost': {
        'uri': '/api/vhosts/{name}',
        'method': 'get',
        'mandatory': ['name'],
        'option': {'columns': ['name', 'messages']},
    },
    'get_user': {'uri': '/api/users/{name}', 'method': 'get', 'mandatory': ['name']},
    'get_permission': {
        'uri': '/api/permissions/{vhost}/{user}',
        'method': 'get',
        'mandatory': ['vhost', 'user'],
    },
    ## listable
    'list_exchange': {
        'uri': '/api/exchanges/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'type']},
    },
    'list_queue': {
        'uri': '/api/queues/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'messages']},
    },
    'list_binding': {
        'uri': '/api/bindings/{vhost}',
        'method': 'get',
        'option': {'columns': ['source', 'destination', 'routing_key']},
    },
    'list_vhost': {
        'uri': '/api/vhosts/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'messages']},
    },
    'list_user': {'uri': '/api/users/', 'method': 'get'},
    'list_permission': {'uri': '/api/users/{user}/permissions', 'method': 'get'},
    'list_consumer': {'uri': '/api/consumers/{vhost}', 'method': 'get'},
    'list_channel': {
        'uri': '/api/channels/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'user']},
    },
    'list_connection': {
        'uri': '/api/connections/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'user', 'channels']},
    },
    'list_node': {
        'uri': '/api/nodes/{vhost}',
        'method': 'get',
        'option': {'columns': ['name', 'type', 'mem_used']},
    },
    ## declarable
    'declare_exchange': {
        'uri': '/api/exchanges/{vhost}/{name}',
        'method': 'put',
        'mandatory': ['name', 'type'],
        'option': {
            'type': 'direct',
            'auto_delete': False,
            'durable': True,
            'internal': False,
            'arguments': {},
        },
    },
    'declare_queue': {
        'uri': '/api/queues/{vhost}/{name}',
        'method': 'put',
        'mandatory': ['name'],
        'option': {
            'auto_delete': False,
            'durable': True,
            'arguments': {},
            'queue_type': None,
        },
    },
    'declare_binding': {
        'uri': '/api/bindings/{vhost}/e/{source}/{destination_char}/{destination}',
        'method': 'post',
        'mandatory': ['source', 'destination'],
        'option': {'destination_type': 'queue', 'routing_key': '', 'arguments': {}},
    },
    'declare_vhost': {
        'uri': '/api/vhosts/{name}',
        'method': 'put',
        'mandatory': ['name'],
        'option': {'tracing': None},
    },
    'declare_user': {
        'uri': '/api/users/{name}',
        'method': 'put',
        'mandatory': ['name', ['password', 'password_hash'], 'tags'],
        'option': {'hashing_algorithm': None, 'tags': {}},
    },
    'declare_permission': {
        'uri': '/api/permissions/{vhost}/{user}',
        'method': 'put',
        'mandatory': ['vhost', 'user', 'configure', 'write', 'read'],
        'option': {'configure': '', 'write': '', 'read': ''},
    },
    ## deletable
    'delete_exchange': {
        'uri': '/api/exchanges/{vhost}/{name}',
        'method': 'delete',
        'mandatory': ['name'],
    },
    'delete_queue': {
        'uri': '/api/queues/{vhost}/{name}',
        'method': 'delete',
        'mandatory': ['name'],
    },
    'delete_binding': {
        'uri': '/api/bindings/{vhost}/e/{source}/{destination_char}/{destination}/{properties_key}',
        'method': 'delete',
        'mandatory': ['source', 'destination_type', 'destination'],
        'option': {'properties_key': '~'},
    },
    'delete_vhost': {
        'uri': '/api/vhosts/{name}',
        'method': 'delete',
        'mandatory': ['name'],
    },
    'delete_user': {
        'uri': '/api/users/{name}',
        'method': 'delete',
        'mandatory': ['name'],
    },
    'delete_permission': {
        'uri': '/api/permissions/{vhost}/{user}',
        'method': 'delete',
        'mandatory': ['vhost', 'user'],
    },
    ## message
    'publish_message': {
        'uri': '/api/exchanges/{vhost}/{exchange}/publish',
        'method': 'post',
        'mandatory': ['routing_key', 'properties'],
        'option': {'routing_key': '', 'properties': {}},
    },
    'get_message': {
        'uri': '/api/queues/{vhost}/{queue}/get',
        'method': 'post',
        'mandatory': ['queue', 'count', 'ackmode', 'encoding'],
        'option': {'count': 5, 'ackmode': 'ack_requeue_false', 'encoding': 'auto'},
    },
    'purge_message': {
        'uri': '/api/queues/{vhost}/{name}/contents',
        'method': 'delete',
        'mandatory': ['name'],
    },
    ## others
    'import_definition': {
        'uri': '/api/definitions/{vhost}',
        'method': 'post',
        'mandatory': [],
    },
    'export_definition': {
        'uri': '/api/definitions/{vhost}',
        'method': 'get',
        'mandatory': [],
    },
    'close_connection': {
        'uri': '/api/connections/{name}',
        'method': 'delete',
        'mandatory': ['name'],
    },
}


class YujianError(Exception):
    pass


class Client:
    async def init(self, base_url, user='guest', password='guest'):
        self.default_option = {'vhost': '%2F'}
        self.http = await Http().init(base_url, user, password)
        return self

    async def close(self):
        await self.http.destroy()

    async def overview(self):
        return await self.invoke(get_func_name())

    async def whoami(self):
        return await self.invoke(get_func_name())

    async def get_queue(self, name: str, vhost: str = None):
        return await self.invoke(get_func_name(), name=name, vhost=vhost)

    async def list_queue(self, vhost: str = None, columns: list[str] = None, **kwargs):
        return await self.invoke(get_func_name(), vhost=vhost, columns=columns, **kwargs)

    async def declare_queue(self, name: str, vhost: str = None, **kwargs):
        return await self.invoke(get_func_name(), name=name, vhost=vhost, **kwargs)

    async def delete_queue(self, name: str, vhost: str = None):
        return await self.invoke(get_func_name(), name=name, vhost=vhost)

    async def get_exchange(self, name: str, vhost: str = None):
        return await self.invoke(get_func_name(), name=name, vhost=vhost)

    async def list_exchange(self, vhost: str = None, columns: list[str] = None, **kwargs):
        return await self.invoke(get_func_name(), vhost=vhost, columns=columns, **kwargs)

    async def declare_exchange(
        self, name: str, type: str = None, vhost: str = None, **kwargs
    ):
        return await self.invoke(
            get_func_name(), name=name, type=type, vhost=vhost, **kwargs
        )

    async def delete_exchange(self, name: str, vhost: str = None):
        return await self.invoke(get_func_name(), name=name, vhost=vhost)

    async def get_binding(
        self,
        source: str,
        destination: str,
        destination_type: str = None,
        properties_key: str = None,
        vhost: str = None,
    ):
        return await self.invoke(
            get_func_name(),
            source=source,
            destination=destination,
            destination_type=destination_type,
            properties_key=properties_key,
            vhost=vhost,
        )

    async def list_binding(self, vhost: str = None, columns: list[str] = None, **kwargs):
        return await self.invoke(get_func_name(), vhost=vhost, columns=columns, **kwargs)

    async def declare_binding(
        self,
        source: str,
        routing_key: str,
        destination: str,
        destination_type: str = None,
        vhost: str = None,
        **kwargs,
    ):
        return await self.invoke(
            get_func_name(),
            source=source,
            routing_key=routing_key,
            destination=destination,
            destination_type=destination_type,
            vhost=vhost,
            **kwargs,
        )

    async def delete_binding(
        self,
        source: str,
        destination: str,
        destination_type: str = None,
        properties_key: str = None,
        vhost: str = None,
    ):
        return await self.invoke(
            get_func_name(),
            source=source,
            destination=destination,
            destination_type=destination_type,
            properties_key=properties_key,
            vhost=vhost,
        )

    async def get_vhost(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def list_vhost(self, vhost: str = None, **kwargs):
        return await self.invoke(get_func_name(), vhost=vhost, **kwargs)

    async def declare_vhost(self, name: str, **kwargs):
        return await self.invoke(get_func_name(), name=name, **kwargs)

    async def delete_vhost(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def get_user(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def list_user(self):
        return await self.invoke(get_func_name())

    async def declare_user(
        self, name: str, password: str = None, tags: list[str] = None, **kwargs
    ):
        return await self.invoke(
            get_func_name(), name=name, password=password, tags=tags, **kwargs
        )

    async def delete_user(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def get_permission(self, user: str, vhost: str = None):
        return await self.invoke(get_func_name(), user=user, vhost=vhost)

    async def list_permission(self, user: str):
        return await self.invoke(get_func_name(), user=user)

    async def declare_permission(
        self,
        user: str,
        vhost: str = None,
        configure: str = None,
        write: str = None,
        read: str = None,
    ):
        return await self.invoke(
            get_func_name(),
            user=user,
            vhost=vhost,
            configure=configure,
            write=write,
            read=read,
        )

    async def delete_permission(self, user: str, vhost: str = None):
        return await self.invoke(get_func_name(), user=user, vhost=vhost)

    async def publish_message(
        self,
        payload: str,
        routing_key: str = None,
        properties: dict = None,
        exchange: str = None,
        vhost: str = None,
        **kwargs,
    ):
        return await self.invoke(
            get_func_name(),
            payload=payload,
            routing_key=routing_key,
            properties=properties,
            exchange=exchange,
            vhost=vhost,
            **kwargs,
        )

    async def get_message(
        self,
        queue: str,
        count: int = None,
        ackmode: str = None,
        encoding: str = None,
        vhost: str = None,
        **kwargs,
    ):
        return await self.invoke(
            get_func_name(),
            queue=queue,
            count=count,
            ackmode=ackmode,
            encoding=encoding,
            vhost=vhost,
            **kwargs,
        )

    async def purge_message(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def list_consumer(self, vhost: str = None):
        return await self.invoke(get_func_name(), vhost=vhost)

    async def list_channel(self, vhost: str = None):
        return await self.invoke(get_func_name(), vhost=vhost)

    async def list_connection(self, vhost: str = None):
        return await self.invoke(get_func_name(), vhost=vhost)

    async def list_node(self, vhost: str = None):
        return await self.invoke(get_func_name(), vhost=vhost)

    async def import_definition(self, vhost: str, **kwargs):
        return await self.invoke(get_func_name(), vhost=vhost, **kwargs)

    async def export_definition(self, vhost: str):
        return await self.invoke(get_func_name(), vhost=vhost)

    async def close_connection(self, name: str):
        return await self.invoke(get_func_name(), name=name)

    async def invoke(self, act: str, **kwargs):
        prop = config.get(act, None)
        if not prop:
            raise YujianError(f'do not support {act}')

        uri, method, payload = self._prepare(prop, kwargs)
        logger.info('{} {} {}', method, uri, payload)
        return await self.http[method](uri, json=payload)

    def _prepare(self, prop, kwargs):
        kwargs = self._merge_option(prop.get('option', {}), kwargs)

        uri = prop.get('uri', None)
        if not uri:
            raise YujianError('uri is None')
        method = prop.get('method', None)
        if not method:
            raise YujianError('method is None')

        if mandatory := prop.get('mandatory', None):
            self._check_mandatory(mandatory, kwargs)

        if 'destination_type' in kwargs.keys():
            kwargs['destination_char'] = kwargs['destination_type'][0]

        for k, v in kwargs.items():
            if isinstance(v, list):
                kwargs[k] = ','.join(v)

        if columns := kwargs.pop('columns', None):
            uri += f'?columns={columns}'
        if sort := kwargs.pop('sort', None):
            uri += f'&sort={sort}'
        if sort_reverse := kwargs.pop('sort_reverse', None):
            uri += f'&sort_reverse={sort_reverse}'

        uri = uri.format(**kwargs)
        payload = kwargs

        return uri, method, payload

    def _check_mandatory(self, mandatory, kwargs):
        for m in mandatory:
            if isinstance(m, list):
                if set(m) & set(kwargs.keys()):
                    continue
                raise YujianError(f'{m} is mandatory')
            else:
                if m in (kwargs.keys()):
                    continue
                raise YujianError(f'{m} is mandatory')
        return True

    def _merge_option(self, option, kwargs):
        option.update(self.default_option)
        option.update({k: v for k, v in kwargs.items() if v is not None})
        return option

    def __getattr__(self, method: str):
        async def act(**kwargs):
            return await self.invoke(method, **kwargs)

        return act


def get_func_name():
    return inspect.stack()[1][3]
