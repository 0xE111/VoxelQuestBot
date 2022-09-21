from dataclasses import dataclass, field
from functools import partialmethod
from logging import getLogger
from typing import ClassVar

import requests
from tenacity import TryAgain, retry, stop_after_attempt, wait_incrementing

log = getLogger(__name__)


class TooManyIterations(Exception):
    pass


@dataclass
class LocatorAPIv1:
    key: str
    session: requests.Session = field(default_factory=requests.Session)
    adapter: requests.adapters.HTTPAdapter = requests.adapters.HTTPAdapter(
        pool_maxsize=32,
    )

    API_URL: ClassVar[str] = 'http://94.228.125.235:8000/api/v1'
    TIMEOUT: ClassVar[int] = 10

    def __post_init__(self):
        self.session.mount('http://', self.adapter)

    @retry(
        reraise=True,
        wait=wait_incrementing(start=1, increment=2),
        stop=stop_after_attempt(20),
    )
    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        if path.startswith('/'):
            path = self.API_URL + path

        kwargs.setdefault('timeout', self.TIMEOUT)
        response = self.session.request(method, path, **kwargs)

        if response.status_code == requests.codes.too_many_requests:
            raise TryAgain()

        return response

    get = partialmethod(request, 'get')
    post = partialmethod(request, 'post')

    def get_devices(self) -> list[dict]:
        response = self.get('/devices/')
        response.raise_for_status()
        return response.json()['devices']
