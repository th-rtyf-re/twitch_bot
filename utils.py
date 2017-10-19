# utils.py

import aiohttp
import itertools


async def request(url, headers):
    """ Asynchronously request an url.

    :param url: The url to request
    :param headers: HTTP headers to request with
    :return: request body, status code
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            status_code = resp.status
            return await resp.text(), status_code


def reduce_dict(dictionary_to_reduce, keys):
    """ Reduce a dictionary to the given keys.

    :param dictionary_to_reduce: dictionary to reduce
    :param keys: keys to keep in the dictionary
    :return: reduced dictionary
    """
    return {key: dictionary_to_reduce[key] for key in keys}


def flatten_dict_values(dictionary):
    """ Return the list of the dictionary values.

    :param dictionary: dictionary whose values are used
    :return: 1D list of dictionary values
    """
    return list(itertools.chain.from_iterable(dictionary.values()))
