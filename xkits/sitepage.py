# coding:utf-8

from base64 import b64encode
from datetime import datetime
from enum import Enum
import os
from typing import Dict
from typing import Optional
from typing import Union
from urllib.parse import ParseResult
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from bs4 import BeautifulSoup
from requests import Response
from requests import Session

from xkits.cache import CacheMiss
from xkits.cache import CachePool
from xkits.cache import CacheTimeUnit

SessionTimeUnit = Union[float, int]
SessionTimeout = Optional[SessionTimeUnit]


class ProxyProtocol(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxySession(Session):

    def __init__(self, protocol: ProxyProtocol, host: str, port: int):
        if not isinstance(protocol, ProxyProtocol):
            raise ValueError(f"Invalid proxy protocol: {protocol}")
        proxies = {
            "http": f"{protocol.value}://{host}:{port}",
            "https": f"{protocol.value}://{host}:{port}",
        }
        super(ProxySession, self).__init__()  # pylint: disable=R1725
        self.proxies.update(proxies)

    @classmethod
    def http_proxy(cls, host: str, port: int = 80) -> "ProxySession":
        return cls(ProxyProtocol.HTTP, host, port)

    @classmethod
    def https_proxy(cls, host: str, port: int = 443) -> "ProxySession":
        return cls(ProxyProtocol.HTTPS, host, port)

    @classmethod
    def socks4_proxy(cls, host: str, port: int = 1080) -> "ProxySession":
        return cls(ProxyProtocol.SOCKS4, host, port)

    @classmethod
    def socks5_proxy(cls, host: str, port: int = 1080) -> "ProxySession":
        return cls(ProxyProtocol.SOCKS5, host, port)


class PageConnect(object):  # pylint: disable=useless-object-inheritance
    '''Website page without cached response'''

    def __init__(self, url: str, session: Session, timeout: SessionTimeout = None):  # noqa:E501
        self.__timeout: SessionTimeout = timeout
        self.__session: Session = session
        self.__url: str = url

    def __str__(self) -> str:
        return f"page object at {id(self)} url={self.url}"

    @property
    def url(self) -> str:
        return self.__url

    @property
    def session(self) -> Session:
        return self.__session

    @property
    def timeout(self) -> SessionTimeout:
        return self.__timeout

    def get(self, timeout: SessionTimeout = None) -> Response:
        response = self.session.get(self.url, timeout=timeout or self.timeout)
        response.raise_for_status()
        return response


class Page(PageConnect):
    '''Website page with cached response'''

    def __init__(self, url: str, session: Optional[Session] = None, timeout: SessionTimeout = None):  # noqa:E501
        super().__init__(url=url, session=session or Session(), timeout=timeout)  # noqa:E501
        self.__response: Optional[Response] = None

    @property
    def label(self) -> str:
        encode: bytes = self.url.encode(encoding="utf-8")
        decode: str = b64encode(encode).decode(encoding="utf-8").rstrip("=")
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{decode}"

    @property
    def response(self) -> Response:
        if self.__response is None:
            self.__response = self.get()
        return self.__response

    @property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.response.content, "html.parser")

    def save(self, path: Optional[str] = None) -> str:
        file: str = self.label if path is None else os.path.join(path, self.label) if os.path.isdir(path) else path  # noqa:E501
        with open(file=file, mode="wb") as hdl:
            hdl.write(self.response.content)
        return file


class PageCache(CachePool[str, Page]):
    '''Website pages cache pool'''

    def __init__(self, session: Optional[Session] = None,
                 lifetime: CacheTimeUnit = 0):
        self.__session: Optional[Session] = session
        super().__init__(lifetime=lifetime)

    def __str__(self) -> str:
        return f"website pages cache pool at {id(self)}"  # pragma: no cover

    def __getitem__(self, url: str) -> Page:
        return self.fetch(url=url)

    @property
    def session(self) -> Session:
        return self.__session or Session()

    def fetch(self, url: str, session: Optional[Session] = None,
              timeout: SessionTimeout = None) -> Page:
        while True:
            try:
                return super().get(url)
            except CacheMiss:
                page = Page(url=url, session=session or self.session,
                            timeout=timeout)
                super().put(url, page)


class Site(PageCache):
    '''Website with pages cache pool'''

    def __init__(self, base: str, session: Optional[Session] = None,
                 lifetime: CacheTimeUnit = 0):
        super().__init__(session=session, lifetime=lifetime)
        components: ParseResult = urlparse(url=base)
        self.__baseurl: str = urlunparse(components)
        self.__components: ParseResult = components

    def __str__(self) -> str:
        return f"website {self.base} with pages cache pool"

    @property
    def scheme(self) -> str:
        return self.__components.scheme

    @property
    def netloc(self) -> str:
        return self.__components.netloc

    @property
    def main(self) -> str:
        '''main page url'''
        return urlunparse((self.scheme, self.netloc, '', '', '', ''))

    @property
    def base(self) -> str:
        '''base url'''
        return self.__baseurl

    def parse(self, *path: str) -> str:
        '''parse page url'''
        site: str = "/".join([self.__components.path] + list(path))
        return urljoin(base=self.main, url=site)

    def login(self, url: str, data: Dict[str, str]) -> Response:
        response = self.session.post(url=url, data=data)
        return response

    def page(self, *path: str, timeout: SessionTimeout = None) -> Page:
        return self.fetch(url=self.parse(*path), session=self.session, timeout=timeout)  # noqa:E501
