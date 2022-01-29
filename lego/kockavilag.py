import re

import requests
from lxml import html


class KockaVilag:
    BASE_URL = "https://kockavilag.hu"
    URL = "{base}/kereses?search[keyword]={article_number}&keyword_submit.x=0&keyword_submit.y=0"
    SHIPPING = 2000
    SHIPPING_FREE = None

    def parse(self, article_number):
        url = self.URL.format(base=self.BASE_URL, article_number=article_number)
        req = requests.get(url)
        cont = req.content
        tree = html.fromstring(cont)
        price = tree.xpath("//*[@id='product']//*[contains(@class,'pricenum')]/text()")
        price = float(re.sub(r'[^0-9]*', '', price[0]))
        return req.url, price


if __name__ == '__main__':
    print(KockaVilag().parse('76902'))
