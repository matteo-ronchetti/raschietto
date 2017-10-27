from raschietto import Raschietto, Matcher
import unittest
import os


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class Test(unittest.TestCase):
    def _test_page_1(self, page):
        self.assertEqual(Matcher("a#link")(page), "link text")
        self.assertEqual(Matcher.link("a#link")(page), "http://url.com")
        self.assertEqual(Matcher.image("img")(page), "http://url.com/image.jpg")
        self.assertEqual(Matcher("div.text")(page), "This is a sample of bold text")

        self.assertEqual(Matcher.link("a.relative")(page, multiple=True), ['http://matteo-ronchetti.github.io/relative_link', 'http://matteo-ronchetti.github.io/raschietto/pages/relative_link'])

        # self.assertEqual(Matcher.link("a.relative", domain="http://url.com")(page), "http://url.com/relative_link")
        # self.assertEqual(Matcher.link("a.relative", domain="http://url.com")(page), "http://url.com/relative_link")

    def test_local_page_loading(self):
        page = Raschietto.from_file(os.path.join(CURRENT_PATH, "..", "pages", "1.html"), "http://matteo-ronchetti.github.io/raschietto/pages/1.html")
        self._test_page_1(page)

    def test_remote_page_loading(self):
        page = Raschietto.from_url("http://matteo-ronchetti.github.io/raschietto/pages/1.html")
        self._test_page_1(page)



