import json
import os

__dir__ = os.path.relpath(os.path.dirname(__file__))
config_file = '{dir}/../config.json'.format(dir=__dir__)


def get():
    if not os.path.exists(config_file):
        return {}
    else:
        with open(config_file) as cf:
            return json.load(cf)
