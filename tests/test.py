from raschietto import Raschietto, Matcher
import unittest
import os


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class Test(unittest.TestCase):
    def test_page_loading(self):
        page = Raschietto.from_file(os.path.join(CURRENT_PATH, "pages", "1.html"))

        self.assertEqual(Matcher("a#link")(page), "link text")
        self.assertEqual(Matcher.link("a#link")(page), "http://url.com")
        self.assertEqual(Matcher.image("img")(page), "http://url.com/image.jpg")
        self.assertEqual(Matcher("div.text")(page), "This is a sample of bold text")

