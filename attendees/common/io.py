import os
from configparser import ConfigParser
from pathlib import Path
from time import sleep


def script_path(*path):
    try:
        return os.path.join(Path(__file__).parents[1], *path)
    except FileNotFoundError:
        return os.path.realpath(os.path.join(*path))


def config(key):
    parser = ConfigParser()
    parser.read(script_path('config.cfg'))
    return parser['DEFAULT'][key]


def load_html(path, callback=None, cb_args=None, cb_kwargs=None, cache=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not cache or not os.path.exists(path):
        response = callback(*cb_args, **cb_kwargs)
        sleep(.3)
        html = response.content
        with open(path, 'wb') as f:
            f.write(html)
    else:
        with open(path, 'rb') as f:
            html = f.read()
    return html
