# PLEASE PUT ALL FUNCTIONS WHICH PERFORM GENERAL FORMATTING ON ANY DATATYPE WITHOUT USING ANY
# MODULES RELATED TO THE EVENT-SYSTEM i.e FUNCTIONS SPECIFIC TO DB MODELS E.G A FUNCTION JUST FOR ROLE_INVITES
import ipaddress
import secrets
import socket
import urllib.parse
import string
import sys

import bleach
from itsdangerous import Serializer
import requests
import re

from app.api.helpers.exceptions import UnprocessableEntity

from flask import current_app


def dasherize(text):
    return text.replace('_', '-')


def require_relationship(resource_list, data):
    for resource in resource_list:
        if resource not in data:
            raise UnprocessableEntity({'pointer': '/data/relationships/{}'.format(resource)},
                                      "A valid relationship with {} resource is required".format(resource))


def string_empty(value):
    return isinstance(value, str) and not value.strip()


def strip_tags(html):
    if html is None:
        return None
    return bleach.clean(html, tags=[], attributes={}, strip=True)


def get_serializer(secret_key=None):
    # Signs email-verification / password-reset tokens, so the key must be secret and unique per deployment
    if secret_key is None:
        from app.settings import get_settings
        secret_key = get_settings()['secret']
    return Serializer(secret_key)


def str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(secrets.choice(chars) for _ in range(size))


# From http://stackoverflow.com/a/3425124
def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def represents_int(value):
    try:
        int(value)
        return True
    except:
        return False


def validate_remote_url(url):
    """
    Only allow http(s) URLs that resolve to public addresses, to prevent
    local file reads (file://) and SSRF against internal services.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('Invalid image URL')
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(parsed.hostname, parsed.port)}
    except socket.gaierror:
        raise ValueError('Invalid image URL')
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise ValueError('Invalid image URL')


def safe_remote_request(method, url, timeout=30, max_redirects=5, **kwargs):
    """
    Performs a request to a user supplied URL. The URL and every redirect target
    have to pass `validate_remote_url`, so redirects cannot be used to reach internal services.
    """
    for _ in range(max_redirects + 1):
        validate_remote_url(url)
        response = requests.request(method, url, allow_redirects=False, timeout=timeout, **kwargs)
        if not response.is_redirect:
            return response
        url = urllib.parse.urljoin(url, response.headers['Location'])
    raise ValueError('Too many redirects')


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    try:
        h = safe_remote_request('HEAD', url)
    except (ValueError, requests.RequestException):
        return False
    header = h.headers
    content_type = header.get('content-type')
    # content_length = header.get('content-length', 1e10)
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def get_filename_from_cd(cd):
    """
    Get filename and ext from content-disposition
    """
    if not cd:
        return '', ''
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return '', ''
    fn = fname[0].rsplit('.', 1)
    return fn[0], '' if len(fn) == 1 else ('.' + fn[1])


def write_file(file, data):
    """simple write to file"""
    fp = open(file, 'w')
    fp.write(str(data, 'utf-8'))
    fp.close()


def update_state(task_handle, state, result=None):
    """
    Update state of celery task
    """
    if result is None:
        result = {}
    if not current_app.config.get('CELERY_ALWAYS_EAGER'):
        task_handle.update_state(
            state=state, meta=result
        )

static_page = 'https://eventyay.com/'
image_link = 'https://www.gstatic.com/webp/gallery/1.jpg'

# store task results in case of testing
# state and info
TASK_RESULTS = {}


class EmptyObject(object):
    pass
