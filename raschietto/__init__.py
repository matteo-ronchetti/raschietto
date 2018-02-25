# coding=utf-8
import requests
import json
import urllib
import urllib.request
import lxml.etree
import lxml.html
import urllib.parse
from lxml.cssselect import CSSSelector
from abc import ABC, abstractmethod


class Matcher:
    def __init__(self, selector, condition=None, mapping=None):
        self.selector = CSSSelector(selector)
        if mapping is not None:
            self.mapping = mapping
        else:
            self.mapping = lambda x, page: x.text_content().strip()

        self.condition = condition

    @staticmethod
    def image(selector, mapping=None):
        if mapping:
            return Matcher(selector, mapping=lambda x, page: mapping(page.get_absolute_url(x.get("src")), page))
        return Matcher(selector, mapping=lambda x, page: page.get_absolute_url(x.get("src")))

    @staticmethod
    def link(selector, startswith=None):
        def mapping(x, page):
            x = page.get_absolute_url(x.get("href"))

            if startswith and not x.startswith(startswith):
                x = None
            return x

        return Matcher(selector, mapping=mapping)

    def __call__(self, item, multiple=False, filter_none=True, page=None):
        if isinstance(item, lxml.html.HtmlElement):
            matches = self.selector(item)
        else:
            matches = self.selector(item.tree)
            page = item

        if self.condition:
            matches = [x for x in matches if self.condition(x)]

        if multiple:
            matches = [self.mapping(x, page) for x in matches]
            if filter_none:
                matches = [x for x in matches if x is not None]
            return matches
        else:
            while matches:
                x = matches.pop()
                if self.mapping:
                    x = self.mapping(x, page)
                if x is not None:
                    return x
            return None


class Raschietto:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

    def __init__(self, html_code, url=""):
        self.tree = lxml.html.fromstring(html_code)
        self.url = url

    @staticmethod
    def from_url(url):
        r = requests.get(url, headers={'User-Agent': Raschietto.user_agent})

        return Raschietto(r.content, url)

    @staticmethod
    def from_file(file_path, url=""):
        f = open(file_path)
        return Raschietto(f.read(), url)

    @staticmethod
    def download_file(url, path):
        req = urllib.request.Request(url, headers={'User-Agent': Raschietto.user_agent})
        resource = urllib.request.urlopen(req)
        with open(path, "wb") as of:
            of.write(resource.read())
        return path

    @staticmethod
    def get_json(url):
        req = urllib.request.Request(url, headers={'User-Agent': Raschietto.user_agent})
        resource = urllib.request.urlopen(req)
        res = resource.read().decode()
        print(res)
        return json.loads(res)

    @staticmethod
    def element_to_text(el):
        return el.text_content().strip()

    def get_absolute_url(self, url):
        return urllib.parse.urljoin(self.url, url)

    @staticmethod
    def _create_matcher(x):
        if isinstance(x, Matcher):
            return x
        if isinstance(x, str):
            return Matcher(x)

        raise ValueError("Extract config matcher should be a Matcher or a String")

    def match(self, x):
        matcher = self._create_matcher(x)
        return matcher(self)

    def match_all(self, x):
        matcher = self._create_matcher(x)
        return matcher(self, multiple=True)

    def extract(self, config):
        res = dict()
        if "single" in config:
            for key in config["single"]:
                matcher = self._create_matcher(config["single"][key])
                res[key] = matcher(self)
        if "list" in config:
            for key in config["list"]:
                matcher = self._create_matcher(config["list"][key])
                res[key] = matcher(self, multiple=True)
        if "multi-item" in config:
            tmp = {}
            for key in config["multi-item"]:
                matcher = self._create_matcher(config["multi-item"][key])
                tmp[key] = matcher(self, multiple=True, filter_none=False)

            res["multi-item"] = [dict(zip(tmp, t)) for t in zip(*tmp.values())]

        return res


class Crawler(ABC):
    def __init__(self, pages):
        if isinstance(pages, str):
            pages = [pages]

        self.pages = pages
        self.visited_pages = set(self.pages)

    @abstractmethod
    def parse_page(self, page):
        pass

    def run(self):
        while self.pages:
            url = self.pages.pop()
            try:
                page = Raschietto.from_url(url)
                new_pages = self.parse_page(page)

                for np in new_pages:
                    if np not in self.visited_pages:
                        self.visited_pages.add(np)
                        self.pages.append(np)

            except Exception as e:
                print("Got error ", e, "while processing page '%s'" % url)
