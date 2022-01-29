import re

import requests
from lxml import html


class KockaAruhaz:
    BASE_URL = "https://www.kockaaruhaz.hu"
    URL = "{base}/kereses?search_keywords={article_number}"
    SHIPPING = 999
    SHIPPING_FREE = None

    def parse(self, article_number):
        url = self.URL.format(base=self.BASE_URL, article_number=article_number)
        cont = requests.get(url).content
        tree = html.fromstring(cont)
        boxes = tree.xpath("//a[contains(@class,'product_box_inner')]")
        box = None

        for b in boxes:
            url = b.xpath("@href")[0]
            if article_number in url:
                box = b
                break

        if box is None:
            raise Exception('Not found product')

        price = box.xpath("span[contains(@class,'product_list_product_price')]/span/text()")
        price = float(re.sub(r'[^0-9]*', '', price[0]))

        return url, price


if __name__ == '__main__':
    print(KockaAruhaz().parse('76902'))
