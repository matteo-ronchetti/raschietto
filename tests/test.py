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

    def test_local_page_loading(self):
        page = Raschietto.from_file(os.path.join(CURRENT_PATH, "..", "pages", "1.html"))
        self._test_page_1(page)

    def test_remote_page_loading(self):
        page = Raschietto.from_url("http://matteo-ronchetti.github.io/raschietto/pages/1.html")
        self._test_page_1(page)



