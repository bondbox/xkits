# coding:utf-8

from base64 import b64encode
from datetime import datetime
import os
from typing import Dict
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

from bs4 import BeautifulSoup
from requests import Response
from requests import Session

from .cache import CacheMiss
from .cache import CachePool
from .cache import CacheTimeout


class PageSession(object):  # pylint: disable=useless-object-inheritance
    def __init__(self, session: Session):
        self.__session: Session = session

    @property
    def session(self) -> Session:
        return self.__session

    def get(self, url) -> Response:
        response = self.session.get(url)
        response.raise_for_status()
        return response


class Page(PageSession):
    def __init__(self, url: str, session: Optional[Session] = None):
        super().__init__(session=session or Session())
        self.__response: Optional[Response] = None
        self.__url: str = url

    @property
    def url(self) -> str:
        return self.__url

    @property
    def label(self) -> str:
        encode: bytes = self.url.encode(encoding="utf-8")
        decode: str = b64encode(encode).decode(encoding="utf-8").rstrip("=")
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{decode}"

    @property
    def response(self) -> Response:
        if self.__response is None:
            self.__response = self.get(url=self.url)
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
    def __init__(self, session: Optional[Session] = None,
                 lifetime: CacheTimeout = 0):
        self.__session: Optional[Session] = session
        super().__init__(lifetime=lifetime)

    def __getitem__(self, url: str) -> Page:
        return self.fetch(url=url)

    @property
    def session(self) -> Optional[Session]:
        return self.__session

    def fetch(self, url: str, session: Optional[Session] = None) -> Page:
        while True:
            try:
                return super().get(url)
            except CacheMiss:
                page = Page(url=url, session=session or self.session)
                super().put(url, page)


class Site(PageCache):
    def __init__(self, base: str, session: Optional[Session] = None,
                 lifetime: CacheTimeout = 0):
        components = urlparse(url=base)
        self.__session: Session = session or Session()
        self.__scheme: str = components.scheme or "https"
        self.__netloc: str = components.netloc or components.path
        self.__scheme_and_netloc: str = urlunparse((self.scheme, self.netloc, '', '', '', ''))  # noqa:E501
        super().__init__(session=self.session, lifetime=lifetime)

    @property
    def scheme(self) -> str:
        return self.__scheme

    @property
    def netloc(self) -> str:
        return self.__netloc

    @property
    def scheme_and_netloc(self) -> str:
        return self.__scheme_and_netloc

    @property
    def session(self) -> Session:
        return self.__session

    def login(self, url: str, data: Dict[str, str]) -> Response:
        response = self.session.post(url=url, data=data)
        return response

    def page(self, *path: str) -> Page:
        url: str = urljoin(base=self.scheme_and_netloc, url="/".join(path))
        return self.fetch(url=url, session=self.session)
