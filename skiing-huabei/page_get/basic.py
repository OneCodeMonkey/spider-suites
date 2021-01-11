import os
import time
import signal
import requests
from config import headers
from utils import (send_email, getip)
from decorators import (timeout_decorator, timeout)
from config import (get_timeout, get_crawl_interval, get_excp_interval, get_max_retries)
from logger import crawler
from requests.exceptions import ReadTimeout, ConnectionError


TIMEOUT = get_timeout()
INTERVAL = get_crawl_interval()
MAX_RETRIES = get_max_retries()
EXCP_INTERVAL = get_excp_interval()


@timeout(200)
def get_api_result(url, cookies=None, method='GET', data=None, need_proxy=False):
    crawler.info('the crawling url is {}'.format(url))
    count = 0

    while count < MAX_RETRIES:
        try:
            if method == 'GET':
                resp = requests.get(url, headers=headers, cookies=cookies, timeout=TIMEOUT)
            elif method == 'POST':
                resp = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=TIMEOUT)
        except (ReadTimeout, ConnectionError, AttributeError) as e:
            crawler.warning("Exceptions are raised when crawling {}. Here are details:{}".format(url, e))
            count += 1
            time.sleep(EXCP_INTERVAL)
            continue

        if resp.status_code == 200:
            if resp.text:
                api_result = resp.text.encode('utf-8', 'ignore').decode('utf-8')
                crawler.info(resp.headers)
            else:
                count += 1
                continue
        else:
            os.kill(os.getppid(), signal.SIGTERM)

        return api_result
