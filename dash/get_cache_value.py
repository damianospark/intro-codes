import sqlite3
import json
import zlib
import gzip
from icecream import ic
import io
import requests
from datetime import timedelta
from requests_cache import CachedSession
from urllib.parse import urlparse

import hashids
import hashlib

# @rule 짧은 url and filesystem safe string 을 생성해야할 때 사용할 것.


def create_key(request: requests.PreparedRequest, **kwargs) -> str:
    """Generate a custom cache key for the given request"""
    parsed_url = urlparse(request.url)
    # ic(parsed_url.path, parsed_url.params)
    src = f'{parsed_url.path}{parsed_url.query}{parsed_url.params}'
    # ic(src)
    # create a hashids object
    hashids_object = hashids.Hashids()
    # create a hash of the input string
    input_string = src
    input_string_hash = int(hashlib.sha256(input_string.encode()).hexdigest(), 16)
    # encode the hash of the input string to a short string
    short_id = hashids_object.encode(input_string_hash)

    return short_id


cache = CachedSession(
    './kakao_cache',
    backend='sqlite',
    serializer='json',
    use_cache_dir=False,                # Save files in the default user cache dir
    cache_control=True,                # Use Cache-Control response headers for expiration, if available
    expire_after=timedelta(days=60),    # Otherwise expire responses after one day
    allowable_codes=[200, 400],        # Cache 400 responses as a solemn reminder of your failures
    allowable_methods=['GET', 'POST'],  # Cache whatever HTTP methods you want
    ignored_parameters=['api_key'],    # Don't match this request param, and redact if from the cache
    match_headers=['Accept-Language'],  # Cache a different response per language
    stale_if_error=True,               # In case of request errors, use stale cache data if possible
    key_fn=create_key).cache


cnt = 0
for response in cache.responses.values():
    cnt += 1
    content_dict = json.loads(str(response.content, 'utf-8'))

    # ic(response.request.method,
    #    response.request.url,
    #    str(response.content, 'utf-8'),
    #    response.headers,
    #    response.status_code)
    ic(response.request.url)
    ic(content_dict['documents'][0]['address']['address_name'])
    ic(content_dict['documents'][0]['address']['x'])
    ic(content_dict['documents'][0]['address']['y'])
    ic(content_dict)
    if cnt > 0:
        break
