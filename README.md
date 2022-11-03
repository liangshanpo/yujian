# 羽箭 Yujian

一个异步的 RabbitMQ HTTP API 客户端。A asyncio Rabbitmq HTTP API client.

![羽箭](https://github.com/imlzg/image/blob/84e4272984ab9b5becaf5c0e6c2b3e45d5c31c4a/yujian.png)

写这个库的初衷是用在 Jiama 的 console 命令中，用于显示 RPC 的服务端和客户端；但找了一圈，却没有发现一个异步且支持Python3 的库，所以写了这个库。


Rabbitmq 的安装可以使用 docker 方式，具体参见[官网](https://www.rabbitmq.com/download.html)。
```shell
sudo docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.10-management
```

在启用“管理插件”运行后，可以在 http://server-name:15672/api/ 查看 Rabbitmq HTTP API 的内容。



### 安装 Install

``` shell
pip install wangong
```



### 接口 API

#### yujian.api.config
Rabbitmq HTTP API 接口配置字典，键定义客户端方法名称，值定义方法调用的 API 地址、请求方法、必填项、默认值等，如：
```python
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
```
你可以根据需要扩展此配置。



#### client = await Client().init('http://localhost:15672')
客户端初始化方法。



#### await client.close()
客户端销毁方法。



#### await client.declare_queue(name, vhost=None, **kwargs)
- `name` str - 队列名称
- `vhost` str - 队列所属的虚拟机，默认为 `/`
- `kwargs` Any - 其他可用参数，具体参见 [Rabbitmq HTTP API DOC](https://rawcdn.githack.com/rabbitmq/rabbitmq-server/v3.11.2/deps/rabbitmq_management/priv/www/api/index.html)



#### await client.list_queue(vhost, columns, **kwargs)
- `vhost` str - 队列所属的虚拟机，默认为 `/`
- `columns` list[str] - 返回结果中包含的列
- `kwargs` Any - 其他可用参数



#### await delete_queue(name, vhost)
- `name` str - 队列名称
- `vhost` str - 队列所属的虚拟机



#### await client.declare_exchange(name, type, vhost, **kwargs)
- `name` str - 交换机名称
- `type` str - 交换机类型
- `vhost` str - 交换机所属的虚拟机，默认为 `/`
- `kwargs` Any - 其他可用参数，具体参见 [Rabbitmq HTTP API DOC](https://rawcdn.githack.com/rabbitmq/rabbitmq-server/v3.11.2/deps/rabbitmq_management/priv/www/api/index.html)



#### await client.declare_binding(source, routing_key, destination, destination_type, vhost, **kwargs)
- `source` str - 绑定的源，交换机名称
- `routing_key` str - 绑定的路由键
- `destination` str - 绑定的终点，交换机或队列的名称
- `destination_type` str - 绑定的重点类型，exchange 或 queue
- `vhost` str - 绑定所属的虚拟机，默认为 `/`
- `kwargs` Any - 其他可用参数，具体参见 [Rabbitmq HTTP API DOC](https://rawcdn.githack.com/rabbitmq/rabbitmq-server/v3.11.2/deps/rabbitmq_management/priv/www/api/index.html)



#### await client.publish_message(payload, routing_key, properties, exchange, vhost, **kwargs)
- `payload` str - 消息内容
- `routing_key` - 路由键
- `properties` - 消息属性
- `exchange` - 交换机
- `vhost` - 虚拟机
- `kwargs` - 其他可用参数，具体参见 [Rabbitmq HTTP API DOC](https://rawcdn.githack.com/rabbitmq/rabbitmq-server/v3.11.2/deps/rabbitmq_management/priv/www/api/index.html)



#### await client.await client.invoke(act, **kwargs)
- `act` str - 需要执行的动作，对应 yujian.api.config 中的键
- `kwargs` Any - 需要传递的参数



#### client.__getattr__(method)
- `method` str - 方法名称，对应 yujian.api.config 中的键

借助 `__getattr__` 方法，你可以根据 [Rabbitmq HTTP API DOC](https://rawcdn.githack.com/rabbitmq/rabbitmq-server/v3.11.2/deps/rabbitmq_management/priv/www/api/index.html) 的要求任意扩展 `yujian.api.config`，直接以键作为方法名在 `client` 对象上调用。



### 示例 Example

``` python
from loguru import logger

from yujian.api import Client


async def main():
    c = await Client().init('http://192.168.56.109:15672/')

    r20 = await c.whoami()
    r21 = await c.list_exchange(columns=['name'])
    r22 = await c.list_queue(
        columns=['vhost', 'name', 'node', 'messages'], sort='name', sort_reverse='true'
    )
    r23 = await c.list_user()
    r24 = await c.get_user(name='guest')
    r25 = await c.get_vhost(name='%2F')
    r26 = await c.get_permission('guest')
    r27 = await c.get_queue('test_queue_2')

    r30 = await c.invoke('declare_queue', name='test_queue')
    r31 = await c.invoke(
        'list_queue',
        columns=['vhost', 'name', 'node', 'messages'],
        sort='name',
        sort_reverse='true',
    )
    r32 = await c.invoke('delete_queue', name='test_queue')
    r33 = await c.invoke('declare_exchange', name='test_exchange', type='direct')
    r34 = await c.invoke(
        'get_message',
        queue='test_queue',
        count=5,
        ackmode='ack_requeue_true',
        encoding='auto',
    )
    r35 = await c.invoke(
        'publish_message',
        exchange='test_exchange',
        payload='ko ko ko',
        routing_key='test_queue',
        payload_encoding='string',
        properties={},
    )
    r36 = await c.invoke(
        'declare_binding',
        source='test_exchange',
        destination='test_queue',
        destination_type='queue',
        routing_key='test_queue',
    )
    r37 = await c.invoke('whoami')

    await c.close()


if __name__ == '__main__':
    config = {
        'handlers': [
            {
                'sink': sys.stdout,
                'format': '<green>{time:YYYY-MM-DD at HH:mm:ss}</green> {level} <level>{message}</level>',
            },
        ],
    }
    logger.configure(**config)

    asyncio.run(main())


```

### License
[MIT](LICENSE) © Li zhigang