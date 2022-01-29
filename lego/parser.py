import json
import os
import lego
import smtplib

from email.mime.text import MIMEText

from lego import config

cache = {}

__dir__ = os.path.relpath(os.path.dirname(__file__))
data_file = '{dir}/../data.json'.format(dir=__dir__)

if not os.path.exists(data_file):
    with open(data_file, 'w') as df:
        json.dump({}, df)
with open(data_file) as df:
    data = json.load(df)


def start():
    for email in config.get()['parse']:
        send = {'packages': {}, 'products': {}, 'names': []}
        for package in config.get()['parse'][email]:
            print('Parse: {}'.format(package['name']))
            (min_subtotal, min_price) = parse(package['article_numbers'])
            for key in min_subtotal:
                data_key = '{}:{}'.format(email, key)
                if data_key not in data or data[data_key] > (min_subtotal[key][0] + min_subtotal[key][1]):
                    send['packages'][key] = min_subtotal[key]
                    data[data_key] = (min_subtotal[key][0] + min_subtotal[key][1])
                    if package['name'] not in send['names']:
                        send['names'].append(package['name'])
            for article_number in min_price:
                data_key = '{}::{}'.format(email, article_number)
                if data_key not in data or data[data_key] > min_price[article_number][0]:
                    send['products'][article_number] = min_price[article_number]
                    data[data_key] = min_price[article_number][0]
                    if package['name'] not in send['names']:
                        send['names'].append(package['name'])

        if send['packages'] or send['products']:
            send_email(email, send)

    with open(data_file, 'w') as df:
        json.dump(data, df)


def send_email(email, content):
    username = config.get()['email']['user']
    password = config.get()['email']['pass']

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(username, password)

    msg = []

    if content['packages']:
        msg = ['Csomagok', '-' * 50]
        for key in content['packages']:
            package = content['packages'][key]
            msg.append('{}: {:.2f} Ft (+{:.2f} Ft szállítás) - {}'.format(
                key,
                package[0],
                package[1],
                package[2]
            ))

    if content['products']:
        msg.append('\nTermékek')
        msg.append('-' * 50)
        for article_number in content['products']:
            product = content['products'][article_number]
            msg.append('{}: {:.2f} Ft - {}'.format(
                article_number,
                product[0],
                product[2]
            ))

    msg = MIMEText('\n'.join(msg))
    msg['Subject'] = 'Lego változás: {}'.format('|'.join(content['names']))
    msg['From'] = 'mrcsempe@gmail.com'
    msg['To'] = email

    server.sendmail('mrcsempe@gmail.com', email, msg.as_string())
    server.quit()


def parse(article_numbers):
    min_subtotal = {}
    min_price = {}

    for parser in [lego.Kocka, lego.KockaAruhaz, lego.KockaVilag]:
        parser = parser()
        print(parser.BASE_URL, end='\r')
        subtotal = 0
        found = []

        for article_number in article_numbers:
            print('{}: {}'.format(parser.BASE_URL, article_number), end='\r')
            try:
                cache_key = '{}_{}'.format(parser.__class__, article_number)
                (url, price) = cache[cache_key] if cache_key in cache else parser.parse(article_number)
                cache[cache_key] = (url, price)
                subtotal += price
                if article_number not in min_price:
                    min_price[article_number] = None
                if min_price[article_number] is None or min_price[article_number][0] > price:
                    min_price[article_number] = [price, parser.SHIPPING, url]
                found.append(article_number)
            except:
                continue

        shipping = 0 if parser.SHIPPING_FREE is not None and parser.SHIPPING_FREE < subtotal else parser.SHIPPING
        key = ','.join(found)
        if key not in min_subtotal:
            min_subtotal[key] = None
        if min_subtotal[key] is None or min_subtotal[key][0] > (subtotal + shipping):
            min_subtotal[key] = [subtotal, shipping, parser.BASE_URL]
        print()

    return min_subtotal, min_price
