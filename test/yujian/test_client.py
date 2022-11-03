import asyncio
import sys

import pytest

from loguru import logger

from yujian.api import Client


@pytest.fixture(scope='module')
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='module')
async def client():
    config = {
        'handlers': [
            {
                'sink': sys.stdout,
                'format': '<green>{time:YYYY-MM-DD at HH:mm:ss}</green> {level} <level>{message}</level>',
            },
        ],
    }
    logger.configure(**config)
    c = await Client().init('http://192.168.56.109:15672/')
    yield c
    await c.close()


MESSAGE = 'ko ko ko'


async def test_invoke(client):
    r = await client.invoke('overview')
    assert r['rabbitmq_version']


async def test_whoami(client):
    r = await client.whoami()
    assert r['name']


async def test_declare_exchange(client):
    r = await client.declare_exchange('test_exchange', type='direct')
    assert not r


async def test_declare_queue(client):
    r = await client.declare_queue('test_queue', durable=False)
    assert not r


@pytest.mark.depends(on=['test_declare_exchange'])
async def test_declare_binding(client):
    r = await client.declare_binding(
        source='test_exchange',
        destination='test_queue',
        destination_type='queue',
        routing_key='test_queue',
    )
    assert not r


@pytest.mark.depends(on=['test_declare_queue'])
async def test_get_queue(client):
    r = await client.get_queue('test_queue')
    assert r['name'] == 'test_queue'


@pytest.mark.depends(on=['test_declare_queue'])
async def test_list_queue(client):
    r = await client.list_queue()
    assert r[0]['name']


@pytest.mark.depends(on=['test_declare_queue'])
async def test_list_queue_column(client):
    r = await client.list_queue(
        columns=['vhost', 'name', 'node', 'messages'], sort='name', sort_reverse='true'
    )
    assert r[0]['name']


@pytest.mark.depends(on=['test_declare_exchange'])
@pytest.mark.depends(on=['test_declare_queue'])
@pytest.mark.depends(on=['test_declare_binding'])
async def test_publish_message(client):
    r = await client.publish_message(
        exchange='test_exchange',
        payload=MESSAGE,
        routing_key='test_queue',
        payload_encoding='string',
        properties={},
    )
    assert r['routed']


@pytest.mark.depends(on=['test_publish_message'])
async def test_get_message(client):
    r = await client.get_message(
        queue='test_queue', count=1, ackmode='ack_requeue_true', encoding='auto'
    )
    print(r)
    assert isinstance(r, list)
    assert r[0]['payload'] == MESSAGE


@pytest.mark.depends(on=['test_publish_message'])
async def test_purge_message(client):
    r = await client.purge_message('test_queue')
    assert not r


@pytest.mark.depends(on=['test_publish_message'])
async def test_delete_exchange(client):
    r = await client.delete_exchange('test_exchange')
    assert not r


@pytest.mark.depends(on=['test_publish_message'])
async def test_delete_queue(client):
    r = await client.delete_queue('test_queue')
    assert not r


if __name__ == '__main__':
    pytest.main(['-s', '-q'])
