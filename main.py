from time import sleep

from lego import parser, config

if __name__ == '__main__':
    while True:
        parser.start()
        sleep(config.get()['run'])
