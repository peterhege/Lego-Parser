import re

from lxml import html
import requests


class Kocka:
    BASE_URL = "https://www.kocka.hu"
    URL = "{base}/LEGO-{article_number}"
    SHIPPING = 999
    SHIPPING_FREE = 79999

    def parse(self, article_number):
        url = self.URL.format(base=self.BASE_URL, article_number=article_number)
        cont = requests.get(url).content
        tree = html.fromstring(cont)
        price = tree.xpath('//*[@id="ContentPlaceHolder1_lblActionPrice"]/text()')
        price = float(re.sub(r'[^0-9]*', '', price[0]))
        return url, price


if __name__ == '__main__':
    print(Kocka().parse('76901'))
