import json

from functools import wraps

import aiohttp


# 使用 __init__ 作为工厂方法 不要传入任何参数，
# 使用另外一个方法作为初始化方法接收参数 同时可以实现异步初始化 返回self 需提前初始化
def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Http:
    async def init(self, base_url=None, user='', password='', **kwargs):
        auth = aiohttp.BasicAuth(user, password) if user else None
        self.session = aiohttp.ClientSession(base_url, auth=auth, **kwargs)
        return self

    def __getattr__(self, method):
        if method.upper() not in aiohttp.hdrs.METH_ALL:
            return super().__getattribute__(method)

        async def request(url, **kwargs):
            async with self.session.request(method, url, **kwargs) as response:
                if response.status < 200 or response.status > 206:
                    return {}
                data = await response.read()
                if data:
                    return json.loads(data.decode())
                return {}

        return request

    def __getitem__(self, method):
        return getattr(self, method)

    async def destroy(self):
        await self.session.close()
