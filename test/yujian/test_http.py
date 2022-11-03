import asyncio

import pytest

from yujian.http import Http


@pytest.fixture(scope="module")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def http():
    http = await Http().init("http://httpbin.org")
    yield http
    await http.destroy()


async def test_get(http):
    r = await http.get("/get")
    assert r["url"] == "http://httpbin.org/get"


if __name__ == "__main__":
    pytest.main(["-s", "-q"])
