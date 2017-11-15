from raschietto import Raschietto, Matcher, Crawler
from pprint import pprint


class SampleCrawler(Crawler):
    def __init__(self, pages):
        self.user_pages = set()
        super().__init__(pages)

    def parse_page(self, page):
        print("Parsing page %s" % page.url)

        post_matcher = Matcher.link("a", startswith="https://matteo.ronchetti.xyz/raschietto-sample/pages/posts")
        user_matcher = Matcher.link("a", startswith="https://matteo.ronchetti.xyz/raschietto-sample/pages/users")

        post_pages = page.match_all(post_matcher)
        self.user_pages |= set(page.match_all(user_matcher))

        return post_pages


cfg = {
    "single": {
        "name": ".user h2",
        "username": ".user > p:nth-child(2) > b",
        "email": ".user > p:nth-child(3) > b",
        "phone": ".user > p:nth-child(4) > b",
        "company": ".user > p:nth-child(5) > b"
    }
}

if __name__ == "__main__":
    crawler = SampleCrawler("https://matteo.ronchetti.xyz/raschietto-sample/pages/posts/1.html")
    crawler.run()

    users = dict()

    for url in crawler.user_pages:
        page = Raschietto.from_url(url)
        user = page.extract(cfg)
        users[user["username"]] = user

    pprint(users)