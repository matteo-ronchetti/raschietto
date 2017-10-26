# coding=utf-8
import time
import os
import requests
import sys
import json
import urllib
import urllib.request
import lxml.etree
import lxml.html
import lxml.html.clean as clean
from lxml.cssselect import CSSSelector


class Matcher:
    def __init__(self, selector, condition=None, mapping=None):
        self.selector = CSSSelector(selector)
        if mapping is not None:
            self.mapping = mapping
        else:
            self.mapping = lambda x: x.text_content().strip()

        self.condition = condition

    @staticmethod
    def image(selector, mapping=None):
        if mapping:
            return Matcher(selector, mapping=lambda x: mapping(x.get("src")))
        return Matcher(selector, mapping=lambda x: x.get("src"))

    @staticmethod
    def link(selector, domain=None, startswith=None):
        def mapping(x):
            x = x.get("href")
            if domain is not None and not x.startswith(domain):
                x = domain + x
            if startswith and not x.startswith(startswith):
                x = None
            return x

        return Matcher(selector, mapping=mapping)

    def __call__(self, page, multiple=False, filter_none=True):
        matches = self.selector(page.tree)

        if self.condition:
            matches = [x for x in matches if self.condition(x)]

        if multiple:
            matches = [self.mapping(x) for x in matches]
            if filter_none:
                matches = [x for x in matches if x is not None]
            return matches
        else:
            while matches:
                x = matches.pop()
                if self.mapping:
                    x = self.mapping(x)
                if x is not None:
                    return x
            return None


class Raschietto:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

    def __init__(self, html_code):
        self.tree = lxml.html.fromstring(html_code)

    @staticmethod
    def from_url(url):
        r = requests.get(url, headers={'User-Agent': Raschietto.user_agent})
        r.encoding = "utf-8"
        return Raschietto(r.text)

    @staticmethod
    def from_file(file_path):
        f = open(file_path)
        return Raschietto(f.read())

    @staticmethod
    def download_file(url, path):
        req = urllib.request.Request(url, headers={'User-Agent': Raschietto.user_agent})
        resource = urllib.request.urlopen(req)
        with open(path, "wb") as of:
            of.write(resource.read())

    @staticmethod
    def get_json(url):
        req = urllib.request.Request(url, headers={'User-Agent': Raschietto.user_agent})
        resource = urllib.request.urlopen(req)
        res = resource.read().decode()
        print(res)
        return json.loads(res)

    # @staticmethod
    # def get_pages(pages, path, delay=0.3):
    #     if not os.path.exists(path):
    #         os.makedirs(path)
    #
    #     with open(os.path.join(path, "list"), 'w') as reference_file:
    #         print("Downloading %d pages to %s" % (len(pages), path))
    #
    #         for i in range(len(pages)):
    #             page = pages[i]
    #             reference_file.write(page + "\n")
    #             r = requests.get(page)
    #             r.encoding = "utf-8"
    #             f = open(os.path.join(path, str(i)), 'w')
    #             html = clean.clean_html(r.text)
    #             f.write(html)
    #             f.close()
    #             progress(i+1, len(pages))
    #             time.sleep(delay)  # delay to be respectful with the server

    @staticmethod
    def _create_matcher(x):
        if isinstance(x, Matcher):
            return x
        if isinstance(x, str):
            return Matcher(x)

        raise ValueError("Extract config matcher should be a Matcher or a String")

    def match(self, x):
        matcher = self._create_matcher(x)
        return matcher(self.tree)

    def match_all(self, x):
        matcher = self._create_matcher(x)
        return matcher(self.tree, multiple=True)

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