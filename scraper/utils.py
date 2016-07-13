import asyncio
from functools import partial
from bs4 import BeautifulSoup

RETRY_SLEEP_TIME = 5

def _request(request_func, url, **kwargs):
    return request_func(url, **kwargs).text

async def async_request(request_func, url, **kwargs):
    # An resilient async request, with retrying
    retry_sleep_time = kwargs.pop("retry_sleep_time", RETRY_SLEEP_TIME)
    try:
        return await asyncio.get_event_loop().run_in_executor(None, partial(_request, request_func, url, **kwargs))
    except:
        print("An error has occured, retrying...")
        await asyncio.sleep(retry_sleep_time)
        return await async_request(request_func, url, **kwargs)


def get_viewstates(parsed_html):
    inputs = parsed_html.find_all(
        True, {'name': ['__VIEWSTATE', '__VIEWSTATEGENERATOR']})
    return {tag.get("name", ""): tag.get("value", "") for tag in inputs}
