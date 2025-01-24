# coding:utf-8

import unittest

import mock
from requests import Session

from xkits import Page
from xkits import Site
from xkits import sitepage


class test_site(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_url: str = "https://iptv-org.github.io/api"
        cls.iptv_org_api: Site = Site(cls.base_url, Session())
        cls.cate_url: str = "https://iptv-org.github.io/api/categories.json"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_chech_str(self):
        check: str = f"website {self.iptv_org_api.base} with pages cache pool"
        self.assertEqual(str(self.iptv_org_api), check)

    def test_login(self):
        with mock.patch.object(self.iptv_org_api.session, "post") as mock_post:
            fake_response = mock.MagicMock()
            mock_post.side_effect = [fake_response]
            self.assertIs(self.iptv_org_api.login("test", {}), fake_response)

    def test_categories(self):
        page = self.iptv_org_api.page("categories.json")
        self.assertIs(self.iptv_org_api[self.cate_url], page)
        self.assertIs(self.iptv_org_api.session, page.session)
        self.assertIsInstance(page, Page)
        self.assertIsInstance(page.label, str)
        self.assertEqual(str(page), f"page object at {id(page)} url={self.cate_url}")  # noqa:E501
        with mock.patch.object(page.session, "get") as mock_get:
            fake_response = mock.MagicMock()
            fake_response.content = "unittest"
            mock_get.return_value = fake_response
            with mock.patch.object(sitepage, "open") as mock_open:
                page.save("test.json")
                mock_open.assert_called_once()
            fake_response.raise_for_status.assert_called_once_with()
            with mock.patch.object(sitepage, "BeautifulSoup") as mock_soup:
                fake_soup = mock.MagicMock()
                mock_soup.return_value = fake_soup
                self.assertIs(page.soup, fake_soup)
